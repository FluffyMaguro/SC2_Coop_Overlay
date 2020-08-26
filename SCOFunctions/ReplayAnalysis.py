import os
import mpyq
import json
import time
import traceback

from SCOFunctions.MLogging import logclass
from SCOFunctions.S2Parser import s2_parse_replay
from SCOFunctions.SC2Dictionaries import UnitNameDict, CommanderMastery, UnitAddKillsTo, UnitCompDict, UnitsInWaves, COMasteryUpgrades, HFTS_Units, TUS_Units, prestige_upgrades


amon_forces = ['Amon','Infested','Salamander','Void Shard','Hologram','Moebius', "Ji'nara","Warp Conduit"]
duplicating_units = ['HotSRaptor','MutatorAmonArtanis','HellbatBlackOps','LurkerStetmannBurrowed']
skip_strings = ['placement', 'placeholder', 'dummy','cocoon','droppod',"colonist hut","bio-dome","amon's train","warp conduit"]
revival_types = {'KerriganReviveCocoon':'K5Kerrigan', 'AlarakReviveBeacon':'AlarakCoop','ZagaraReviveCocoon':'ZagaraVoidCoop','DehakaCoopReviveCocoonFootPrint':'DehakaCoop','NovaReviveBeacon':'NovaCoop','ZeratulCoopReviveBeacon':'ZeratulCoop'}
icon_units = {'MULE','Omega Worm','Infested Bunker','Mecha Infestor','Unbound Fanatic','Strike Fighter Platform'}
self_killing_units = {'FenixCoop', 'FenixDragoon', 'FenixArbiter'}
dont_show_created_lost = {'Super Gary','Gary','Tychus Findlay',"James 'Sirius' Sykes","Kev 'Rattlesnake' West",'Nux','Crooked Sam','Lt. Layna Nikara',"Miles 'Blaze' Lewis","Rob 'Cannonball' Boswell","Vega"}
aoe_units = {'Raven','ScienceVessel','Viper','HybridDominator','Infestor','HighTemplar','Blightbringer','TitanMechAssault','MutatorAmonNova'}
tychus_outlaws = {'TychusCoop','TychusReaper','TychusWarhound','TychusMarauder','TychusHERC','TychusFirebat','TychusGhost','TychusSpectre','TychusMedic',}
commander_upgrades = { "AlarakCommander":"Alarak", "ArtanisCommander":"Artanis", "FenixCommander":"Fenix", "KaraxCommander":"Karax", "VorazunCommander":"Vorazun", "ZeratulCommander":"Zeratul", "HornerCommander":"Han & Horner", "MengskCommander":"Mengsk", "NovaCommander":"Nova", "RaynorCommander":"Raynor", "SwannCommander":"Swann", "TychusCommander":"Tychus", "AbathurCommander":"Abathur", "DehakaCommander":"Dehaka", "KerriganCommander":"Kerrigan", "StukovCommander":"Stukov", "ZagaraCommander":"Zagara", "StetmannCommander":"Stetmann"}
commander_no_units = {'Nova':'CoopCasterNova', "Han & Horner":'HHMagneticMine',"Karax":"SoACasterKarax","Artanis":"SoACasterArtanis"}
units_killed_in_morph = {'HydraliskLurker','MutaliskBroodlord','RoachVile','Mutalisk'}
primal_combat_predecessors = {'DehakaRavasaur':'DehakaZerglingLevel2','DehakaRoachLevel3':'DehakaRoachLevel2','DehakaGuardianFightMorph':'DehakaRoachLevel2','ImpalerDehaka':'DehakaHydraliskLevel2','DehakaMutaliskLevel3FightMorph':'DehakaHydraliskLevel2','DehakaPrimalSwarmHost':'DehakaSwarmHost','DehakaUltraliskLevel3':'DehakaUltraliskLevel2'}

logger = logclass('REPA','INFO')


def contains_skip_strings(pname):
    """ Checks if any of skip strings is in the pname """
    lowered_name = pname.lower()
    for item in skip_strings:
        if item in lowered_name:
            return True
    return False


def check_amon_forces(alist, string):
    """ Checks if any word from the list is in the string """
    for item in alist:
        if item in string:
            return True
    return False


def upgrade_is_in_mastery_upgrades(upgrade):
    """ Checks if the upgrade is in mastery upgrades, if yes, returns the Commnader and upgrade index"""
    for co in COMasteryUpgrades:
        if upgrade in COMasteryUpgrades[co]:
            return co, COMasteryUpgrades[co].index(upgrade)
    return False, 0


def prestige_talent_name(upgrade):
    """ Checks if the upgrade is in prestige upgrades. If yes, returns Prestige name"""

    for co in prestige_upgrades:
        if upgrade in prestige_upgrades[co]:
            return prestige_upgrades[co][upgrade]
    return None


def switch_names(pdict):
    """ Changes names to that in unit dictionary, sums duplicates"""
    temp_dict = {}

    for key in pdict:
        # For locusts, broodlings, interceptors, add kills to the main unit. Don't add unit created/lost
        if key in UnitAddKillsTo:
            name = UnitAddKillsTo[key]
            if name in temp_dict:
                temp_dict[name][2] += pdict[key][2]
            else:
                temp_dict[name] = [0,0,pdict[key][2],0]

        else:
            # Translate names & sum up those with the same names
            name = UnitNameDict.get(key,key)
            if name in temp_dict:
                for a in range(len(temp_dict[name])):
                    temp_dict[name][a] += pdict[key][a]
            else:
                temp_dict[name] = list()
                for a in range(len(pdict[key])):
                    temp_dict[name].append(pdict[key][a])

    return temp_dict


def get_enemy_comp(identified_waves):
    """ Takes indentified waves and tries to match them with known enemy AI comps.
        Waves are identified as events where 6+ units were created at the same second. """

    # Each AI gets points for each matching wave
    results = dict()
    for AI in UnitCompDict:
        results[AI] = 0

    # Lets go through our waves, compare them to known AI unit waves
    for iden_wave in identified_waves:
        types = set(identified_waves[iden_wave])
        if len(types) == 0:
            continue

        logger.debug(f'{"-"*40}\nChecking this wave type: {types}\n')
        for AI in UnitCompDict:
            for idx,wave in enumerate(UnitCompDict[AI]):
                # Don't include Medivac, it's removed from wave units as well
                wave.difference_update({'Medivac'})

                # Identical wave
                if types == wave:
                    logger.debug(f'"{AI}" wave {idx+1} is the same: {wave}')
                    results[AI] += 1*len(wave)
                    continue

                # In case of alternate units or some noise
                if types.issubset(wave) and len(wave) - len(types) == 1:
                    logger.debug(f'"{AI}" wave {idx+1} is a close subset: {types} | {wave}')
                    results[AI] += 0.25*len(wave)

    results = {k:v for k,v in sorted(results.items(), key=lambda x:x[1],reverse=True) if v!=0}
    logger.debug(f'{"-"*40}\nAnd results are: {results}')

    # Return the comp with the most points
    if len(results) > 0:
        logger.debug(f'Most likely AI: "{list(results.keys())[0]}" with {100*list(results.values())[0]/sum(results.values()):.1f}% points\n\n')
        return list(results.keys())[0]
    return 'Unidentified AI'


def unitid(event, killer=False):
    """ Returns and unique integer as unit id.
    `killer`=True for killer unique id, otherwise normal unit.
    Assuming index is less than 100000 (usually it's < 1000)
     """
    if killer:
        index = event['m_killerUnitTagIndex']
        recycleindex = event['m_killerUnitTagRecycle']
    else:
        index = event['m_unitTagIndex']
        recycleindex = event['m_unitTagRecycle']

    if index==None or recycleindex==None:
        logger.debug(f'No unitid from {killer=}{event=}')
        return None

    return recycleindex*100000 + index



def analyse_replay(filepath, playernames=['']):
    """ Analyses the replay and returns the analysis"""

    """
    This whole function is a bit messy. It originated in a very different form.
    I should be broken into more functions. Players shouldn't be hardcoded to
    "main" and "ally" but instead a single datastructure. Which player shows on
    top should be decided in javascript and not here.

    """

    # Data structure is {unitType : [#created, #died, #kills, #killfraction]}
    unit_type_dict_main = {}
    unit_type_dict_ally = {}
    unit_type_dict_amon = {}
    logger.info(f'Analysing: {filepath}')

    # Load the replay
    replay = None
    for i in range(2):
        try:
            replay = s2_parse_replay(filepath, return_events=True)
            break
        except:  # You can get an error here if SC2 didn't finish writing into the file. Very rare.
            logger.error(f'Parsing error ({filepath})\n{traceback.format_exc()}')
            time.sleep(0.2)

    if replay == None:
        return {}

    # Find Amon players
    amon_players = set()
    amon_players.add(3)
    amon_players.add(4)
    for player in replay['players']:
        if player['pid'] > 4 and check_amon_forces(amon_forces,player['name']):
            amon_players.add(player['pid'])


    # Find player names and numbers
    main_player = 1
    main_player_found = False

    if len(playernames)>0: # Check if you can find the name in the list
        for player in replay['players']:
            for playeriter in playernames:
                if player['pid'] in [1,2] and main_player_found == False and playeriter.lower() in player.get('name','').lower():
                    main_player = player['pid']
                    main_player_found = True
                    break

    # Ally
    ally_player = 1 if main_player == 2 else 2

    # Start saving data
    replay_report_dict = dict()
    replay_report_dict['filepath'] = filepath
    replay_report_dict['replaydata'] = True
    replay_report_dict['map'] = replay['map_name']
    replay_report_dict['extension'] = replay['extension']
    replay_report_dict['B+'] = replay['brutal_plus']
    replay_report_dict['result'] = replay['result']
    replay_report_dict['main'] = replay['players'][main_player].get('name','None')
    replay_report_dict['ally'] = replay['players'][ally_player].get('name','None')
    replay_report_dict['mainAPM'] = replay['players'][main_player].get('apm',0)
    replay_report_dict['allyAPM'] = replay['players'][ally_player].get('apm',0)

    # Difficulty
    diff_1 = replay['difficulty'][0]
    diff_2 = replay['difficulty'][1]
    if diff_1 == diff_2:
        replay_report_dict['difficulty'] = diff_1
    elif main_player == 1:
        replay_report_dict['difficulty'] = f'{diff_1}/{diff_2}'
    else:
        replay_report_dict['difficulty'] = f'{diff_2}/{diff_1}'

    logger.debug(f'Report dict: {replay_report_dict}')

    # Events
    unit_dict = {} # Data structure is {unit_id : [UnitType, Owner]}; used to track all units
    DT_HT_Ignore = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # Ignore certain amount of DT/HT deaths after archon is initialized. DT_HT_Ignore[player]
    killcounts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    TIME_DEFAULT = 99999999
    START_TIME = replay['start_time']+1 # Add one second for wider margins
    accu_length = replay['accurate_length']
    END_TIME = replay['end_time']
    commander_fallback = dict()
    outlaw_order = []
    wave_units = {'second':0,'units':[]}
    identified_waves = dict()
    mastery_fallback = {1:[0,0,0,0,0,0],2:[0,0,0,0,0,0]}
    killbot_feed = [0,0,0]
    custom_kill_count = dict()
    map_identification = ''
    UsedMutatorSpiderMines = set()
    PrestigeTalents = [None,None,None]

    last_aoe_unit_killed = [0]*17
    for player in range(1,16):
        last_aoe_unit_killed[player] = [None, 0] if player in amon_players else None

    for event in replay['events']:
        # Skip events after the game ended
        if event['_gameloop']/16 > END_TIME:
            continue

        if event['_event'] == 'NNet.Replay.Tracker.SUpgradeEvent' and event['m_playerId'] in [1,2]:
            _upg_name = event['m_upgradeTypeName'].decode()
            _upg_pid = event['m_playerId']

            # Commander fallback (used for arcade maps)
            if _upg_name in commander_upgrades:
                commander_fallback[_upg_pid] = commander_upgrades[_upg_name]

            # Mastery upgrade fallback (used for arcade maps)
            mas_commander, mas_index = upgrade_is_in_mastery_upgrades(_upg_name)
            if mas_commander:
                logger.debug(f'Player {_upg_pid} (com: {mas_commander}) got upgrade {_upg_name} (idx: {mas_index}) (count: {event["m_count"]})')
                mastery_fallback[_upg_pid][mas_index] = event['m_count']

            # Prestige talents
            _prestige = prestige_talent_name(_upg_name)
            if _prestige != None:
                PrestigeTalents[_upg_pid] = _prestige

        if event['_event'] in ['NNet.Replay.Tracker.SUnitBornEvent','NNet.Replay.Tracker.SUnitInitEvent']:
            _unit_type = event['m_unitTypeName'].decode()
            _control_pid = event['m_controlPlayerId']
            unit_dict[unitid(event)] = [_unit_type, _control_pid]

            # Certain hero units don't die, instead lets track their revival beacons/cocoons. Let's assume they will finish reviving.
            if _unit_type in revival_types and _control_pid in [1,2] and event['_gameloop']/16 > START_TIME:
                if _control_pid == main_player:
                    unit_type_dict_main[revival_types[_unit_type]][1] += 1
                    unit_type_dict_main[revival_types[_unit_type]][0] += 1
                if _control_pid == ally_player:
                    unit_type_dict_ally[revival_types[_unit_type]][1] += 1
                    unit_type_dict_ally[revival_types[_unit_type]][0] += 1

            # Identify Dead of Night map
            if _unit_type == 'SensorTower' and _control_pid == 6:
                map_identification = 'Dead of Night'

            # Primal combat fix. For every morph we are substracting two losses from the base unit type
            if _unit_type in primal_combat_predecessors:
                logger.debug(f'{_unit_type} substracting from {primal_combat_predecessors[_unit_type]}\n')
                if main_player == _control_pid:
                    unit_type_dict_main[primal_combat_predecessors[_unit_type]][1] -= 2
                if ally_player == _control_pid:
                    unit_type_dict_ally[primal_combat_predecessors[_unit_type]][1] -= 2

            # Save stats for units created
            if main_player == _control_pid:
                if _unit_type in unit_type_dict_main:
                    unit_type_dict_main[_unit_type][0] += 1
                else:
                    unit_type_dict_main[_unit_type] = [1,0,0,0]

            if ally_player == _control_pid:
                if _unit_type in unit_type_dict_ally:
                    unit_type_dict_ally[_unit_type][0] += 1
                else:
                    unit_type_dict_ally[_unit_type] = [1,0,0,0]

            if _control_pid in amon_players:
                if _unit_type in unit_type_dict_amon:
                    unit_type_dict_amon[_unit_type][0] += 1
                else:
                    unit_type_dict_amon[_unit_type] = [1,0,0,0]

            # Outlaw order
            if _unit_type in tychus_outlaws and _control_pid in [1,2] and not(_unit_type in outlaw_order):
                outlaw_order.append(_unit_type)

            # Identifying waves
            if _control_pid in [3,4,5,6] and event['_gameloop']/16 > START_TIME + 60 and _unit_type in UnitsInWaves:
                if wave_units['second'] == event['_gameloop']/16:
                    wave_units['units'].append(_unit_type)
                else:
                    wave_units['second'] = event['_gameloop']/16
                    wave_units['units'] = [_unit_type]

                if len(wave_units['units']) > 5:
                    identified_waves[event['_gameloop']/16] = wave_units['units']

        # In future ignore some Dark/High Templar deaths caused by Archon merge
        if event['_event'] == 'NNet.Replay.Tracker.SUnitInitEvent' and event['m_unitTypeName'].decode() == "Archon":
            DT_HT_Ignore[event['m_controlPlayerId']] += 2

        if event['_event'] == 'NNet.Replay.Tracker.SUnitTypeChangeEvent' and unitid(event) in unit_dict:
                _old_unit_type = unit_dict[unitid(event)][0]
                _control_pid = unit_dict[unitid(event)][1]
                _unit_type = event['m_unitTypeName'].decode()

                # Strange. Some units morph to egg, then the morph is created, then the egg morphs back and the unit is killed
                if _unit_type in units_killed_in_morph:
                    continue

                # Update unit_dict
                unit_dict[unitid(event)][0] = _unit_type

                # Add to created units
                if _unit_type in UnitNameDict and _old_unit_type in UnitNameDict:

                    if UnitNameDict[_unit_type] != UnitNameDict[_old_unit_type]: #don't add into created units if it's just a morph

                        # Increase unit type created for controlling player
                        if main_player == _control_pid:
                            if _unit_type in unit_type_dict_main:
                                unit_type_dict_main[_unit_type][0] += 1
                            else:
                                unit_type_dict_main[_unit_type] = [1,0,0,0]

                        if ally_player == _control_pid:
                            if _unit_type in unit_type_dict_ally:
                                unit_type_dict_ally[_unit_type][0] += 1
                            else:
                                unit_type_dict_ally[_unit_type] = [1,0,0,0]

                        if _control_pid in amon_players:
                            if _unit_type in unit_type_dict_amon:
                                unit_type_dict_amon[_unit_type][0] += 1
                            else:
                                unit_type_dict_amon[_unit_type] = [1,0,0,0]
                    else:
                        if main_player == _control_pid and not(_unit_type in unit_type_dict_main):
                            unit_type_dict_main[_unit_type] = [0,0,0,0]

                        if ally_player == _control_pid and not(_unit_type in unit_type_dict_ally):
                            unit_type_dict_ally[_unit_type] = [0,0,0,0]

                        if _control_pid in amon_players and not(_unit_type in unit_type_dict_amon):
                            unit_type_dict_amon[_unit_type] = [0,0,0,0]


        # Update ownership
        if event['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent' and unitid(event) in unit_dict:
            unit_dict[unitid(event)][1] = event['m_controlPlayerId']

        # Update some kill stats
        if event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent':
            try:
                _killed_unit_type = unit_dict[unitid(event)][0]
                _losing_player = unit_dict[unitid(event)][1]
                _killing_player = event['m_killerPlayerId']

                # Count kills for players
                if _losing_player != _killing_player and not _killed_unit_type in ['FuelCellPickupUnit','ForceField'] and not(_killing_player in [1,2] and _losing_player in [1,2]) and _killing_player != None: # Don't count team kills
                    killcounts[_killing_player] += 1

                # Get last_aoe_unit_killed (used when player units die without a killing unit, it was likely some enemy caster casting persistent AoE spell)
                if _killed_unit_type in aoe_units and _killing_player in [1,2] and _losing_player in amon_players and unitid(event) != None:
                    last_aoe_unit_killed[_losing_player] = [_killed_unit_type, event['_gameloop']/16]

            except:
                logger.error(traceback.format_exc())

        # More kill stats
        if event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent' and unitid(event) in unit_dict:
            try:
                _killing_unit_id = unitid(event, killer=True)
                _killing_player = event['m_killerPlayerId']
                _killed_unit_type = unit_dict[unitid(event)][0]
                _losing_player = int(unit_dict[unitid(event)][1])

                # Get killing unit
                if _killing_unit_id in unit_dict and unitid(event) != None: # We have a killing unit
                    _killing_unit_type = unit_dict[_killing_unit_id][0]
                else:
                    """
                    For no-unit, check if we default to some commander no-unit like airstrike, or use 'NoUnit'
                    But lets use this only rarely. Units killed in transports count for this as well.
                    Other not counted sources: Dusk Wings lifting off, CoD explosion, ...
                    """
                    _commander = commander_fallback.get(_killing_player,None) #
                    _killing_unit_type = commander_no_units.get(_commander,'NoUnit')

                # Killbot feed
                if _killing_unit_type in ['MutatorKillBot','MutatorDeathBot','MutatorMurderBot'] and _losing_player in [1,2]:
                    killbot_feed[_losing_player] += 1

                # Custom kill count
                if _killing_player in [1,2] and _losing_player in amon_players:
                    if _killed_unit_type in HFTS_Units:
                        if not 'hfts' in custom_kill_count:
                            custom_kill_count['hfts'] = {1:0,2:0}
                        custom_kill_count['hfts'][_killing_player] += 1

                    if _killed_unit_type in TUS_Units:
                        if not 'tus' in custom_kill_count:
                            custom_kill_count['tus'] = {1:0,2:0}
                        custom_kill_count['tus'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorPropagator':
                        if not 'propagators' in custom_kill_count:
                            custom_kill_count['propagators'] = {1:0,2:0}
                        custom_kill_count['propagators'][_killing_player] += 1

                    elif _killed_unit_type in ['MutatorSpiderMine','MutatorSpiderMineBurrowed','WidowMineBurrowed','WidowMine']:
                        if not 'minesweeper' in custom_kill_count:
                            custom_kill_count['minesweeper'] = {1:0,2:0}
                        custom_kill_count['minesweeper'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorVoidRift':
                        if not 'voidrifts' in custom_kill_count:
                            custom_kill_count['voidrifts'] = {1:0,2:0}
                        custom_kill_count['voidrifts'][_killing_player] += 1

                    elif _killed_unit_type in ['MutatorTurkey','MutatorTurking','MutatorInfestedTurkey']:
                        if not 'turkey' in custom_kill_count:
                            custom_kill_count['turkey'] = {1:0,2:0}
                        custom_kill_count['turkey'][_killing_player] += 1

                    elif _killed_unit_type == 'MutatorVoidReanimator':
                        if not 'voidreanimators' in custom_kill_count:
                            custom_kill_count['voidreanimators'] = {1:0,2:0}
                        custom_kill_count['voidreanimators'][_killing_player] += 1

                    elif _killed_unit_type in ['InfestableBiodome','JarbanInfestibleColonistHut','InfestedMercHaven','InfestableHut']:
                        if not 'deadofnight' in custom_kill_count:
                            custom_kill_count['deadofnight'] = {1:0,2:0}
                        custom_kill_count['deadofnight'][_killing_player] += 1

                # If an enemy mutator spider mine kills something, counts a kill for the first player who lost a unit to it
                if _losing_player in [1,2] and _killing_player in amon_players:
                    if _killing_unit_type == 'MutatorSpiderMine' and not _killing_unit_id in UsedMutatorSpiderMines:
                        UsedMutatorSpiderMines.add(_killing_unit_id) # Count each mutator spider mine only once
                        if not 'minesweeper' in custom_kill_count:
                            custom_kill_count['minesweeper'] = {1:0,2:0}
                        custom_kill_count['minesweeper'][_losing_player] += 1

                """Fix kills for some enemy area-of-effect units that kills player units after they are dead.
                   This is the best guess, if one of aoe_units died recently, it was likely that one. """
                if _killing_unit_type == 'NoUnit' and _killing_unit_id == None and _killing_player in amon_players and _losing_player != _killing_player:
                    if event['_gameloop']/16 - last_aoe_unit_killed[_killing_player][1] < 9 and last_aoe_unit_killed[_killing_player][0] != None:
                        unit_type_dict_amon[last_aoe_unit_killed[_killing_player][0]][2] += 1
                        logger.debug(f'{last_aoe_unit_killed[_killing_player][0]}({_killing_player}) killed {_killed_unit_type} | {event["_gameloop"]/16}s')

                # Update unit kill stats
                if ((_killing_unit_id in unit_dict) or _killing_unit_type in commander_no_units.values()) and (_killing_unit_id != unitid(event)) and _losing_player != _killing_player and _killed_unit_type != 'FuelCellPickupUnit':
                    if main_player == _killing_player:
                        if _killing_unit_type in unit_type_dict_main:
                            unit_type_dict_main[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_main[_killing_unit_type] = [0,0,1,0]

                    if ally_player == _killing_player:
                        if _killing_unit_type in unit_type_dict_ally:
                            unit_type_dict_ally[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_ally[_killing_unit_type] = [0,0,1,0]

                    if _killing_player in amon_players and not _losing_player in amon_players:
                        if _killing_unit_type in unit_type_dict_amon:
                            unit_type_dict_amon[_killing_unit_type][2] += 1
                        else:
                            unit_type_dict_amon[_killing_unit_type] = [0,0,1,0]

                # Debug for player no units kills
                if _killed_unit_type not in {'Scarab','Interceptor'} and not _killing_unit_id in unit_dict and not _killing_unit_type in commander_no_units.values() and _killing_player in {1,2} and _losing_player != _killing_player:
                    logger.info(f'{_killing_unit_type} ({_killing_player}|{commander_fallback.get(_killing_player,"")}) killed {_killed_unit_type} ({_losing_player}) - {event["m_x"]}x{event["m_y"]} - {event["_gameloop"]/16:.1f}s ')

                # Update unit death stats
                # Don't count self kills like Fenix switching suits
                if _killed_unit_type in self_killing_units and _killing_player == None:
                    if main_player == _losing_player:
                        unit_type_dict_main[_killed_unit_type][0] -= 1
                    if ally_player == _losing_player:
                        unit_type_dict_ally[_killed_unit_type][0] -= 1
                    continue

                # Fix for units like Raptorlings that are counted each time they jump (as death and birth)
                if event['_gameloop']/16 > 0 and _killed_unit_type in duplicating_units and _killed_unit_type == _killing_unit_type and _losing_player == _killing_player:
                    if main_player == _losing_player:
                        unit_type_dict_main[_killed_unit_type][0] -= 1
                        continue
                    if ally_player == _losing_player:
                        unit_type_dict_ally[_killed_unit_type][0] -= 1
                        continue
                    if _killing_player in amon_players:
                        unit_type_dict_amon[_killed_unit_type][0] -= 1
                        continue

                # In case of death caused by Archon merge, ignore these kills
                if (_killed_unit_type == 'HighTemplar' or _killed_unit_type == 'DarkTemplar') and DT_HT_Ignore[_losing_player] > 0:
                    DT_HT_Ignore[_losing_player] -= 1
                    continue

                # Add deaths
                if main_player == _losing_player and event['_gameloop']/16 > 0 and event['_gameloop']/16 > START_TIME: # Don't count deaths on game init
                    if _killed_unit_type in unit_type_dict_main:
                        unit_type_dict_main[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_main[_killed_unit_type] = [0,1,0,0]

                if ally_player == _losing_player and event['_gameloop']/16 > 0 and event['_gameloop']/16 > START_TIME:
                    if _killed_unit_type in unit_type_dict_ally:
                        unit_type_dict_ally[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_ally[_killed_unit_type] = [0,1,0,0]

                if _losing_player in amon_players and event['_gameloop']/16 > 0 and event['_gameloop']/16 > START_TIME:
                    if _killed_unit_type in unit_type_dict_amon:
                        unit_type_dict_amon[_killed_unit_type][1] += 1
                    else:
                        unit_type_dict_amon[_killed_unit_type] = [0,1,0,0]

            except:
                logger.error(traceback.format_exc())

    # pprint(unit_type_dict_main)
    # pprint(unit_type_dict_ally)
    # pprint(unit_type_dict_amon)
    # logger.info(f'Kill counts: {killcounts}')

    # Save more data to final dictionary
    replay_report_dict['comp'] = get_enemy_comp(identified_waves)
    replay_report_dict['length'] = replay['accurate_length']/1.4

    # Main player
    replay_report_dict['mainCommander'] = replay['players'][main_player].get('commander','')
    replay_report_dict['mainCommanderLevel'] = replay['players'][main_player].get('commander_level',0)
    replay_report_dict['mainMasteries'] = replay['players'][main_player].get('masteries',[0,0,0,0,0,0])
    replay_report_dict['mainkills'] = killcounts[main_player]
    replay_report_dict['mainIcons'] = dict()
    replay_report_dict['mainPrestige'] = PrestigeTalents[main_player]

    # Ally player
    replay_report_dict['allyCommander'] = replay['players'][ally_player].get('commander','')
    replay_report_dict['allyCommanderLevel'] = replay['players'][ally_player].get('commander_level',0)
    replay_report_dict['allyMasteries'] = replay['players'][ally_player].get('masteries',[0,0,0,0,0,0])
    replay_report_dict['allykills'] = killcounts[ally_player]
    replay_report_dict['allyIcons'] = dict()
    replay_report_dict['allyPrestige'] = PrestigeTalents[ally_player]

    # Fallback
    if replay_report_dict['mainCommander'] == '':
        replay_report_dict['mainCommander'] = commander_fallback.get(main_player,"")

    if replay_report_dict['allyCommander'] == '':
        replay_report_dict['allyCommander'] = commander_fallback.get(ally_player,"")

    # MM mastery fallback
    if '[MM]' in filepath:
        replay_report_dict['mainMasteries'] = mastery_fallback[main_player]
        replay_report_dict['allyMasteries'] = mastery_fallback[ally_player]

        # Assume commander level of 15
        replay_report_dict['mainCommanderLevel'] = 15
        replay_report_dict['allyCommanderLevel'] = 15

    # Icons: Tychus' Outlaws
    if replay_report_dict.get('mainCommander', None) == 'Tychus':
        replay_report_dict['mainIcons']['outlaws'] = outlaw_order
    elif replay_report_dict.get('allyCommander', None) == 'Tychus':
        replay_report_dict['allyIcons']['outlaws'] = outlaw_order

    # Icons: Kills
    # First decide between hfts and tus
    if 'tus' in custom_kill_count and 'hfts' in custom_kill_count:
        custom_kill_count['tus'][1] += custom_kill_count['hfts'][1]
        custom_kill_count['tus'][2] += custom_kill_count['hfts'][2]
        del custom_kill_count['hfts']

    for item in ['hfts','tus','propagators','voidrifts','turkey','voidreanimators','deadofnight','minesweeper']:
        if item in custom_kill_count:
            # Skip if it's not a Dead of Night map
            if item == 'deadofnight' and map_identification != 'Dead of Night':
                continue

            # Skip if just mines died, not a mutation
            if item == 'minesweeper' and not 'MutatorSpiderMine' in unit_type_dict_amon:
                continue

            replay_report_dict['mainIcons'][item] = custom_kill_count[item][main_player]
            replay_report_dict['allyIcons'][item] = custom_kill_count[item][ally_player]

    # Don't post if no commander, likely non-coop replay
    if replay_report_dict['mainCommander'] == '':
        logger.error('Not a Co-op replay')


    def fill_unit_kills_and_icons(playername, player, pdict, percent_cutoff=0):
        """ Fills units into output dictionary, fill created/list units into icons """
        new_dict = switch_names(pdict)
        sorted_dict = {k:v for k,v in sorted(new_dict.items(), reverse = True, key=lambda item: item[1][2])} # Sorts by number of create (0), lost (1), kills (2), K/D (3)

        # Save data
        unitkey = 'mainUnits' if player == main_player else 'allyUnits'
        iconkey = 'mainIcons' if player == main_player else 'allyIcons'
        replay_report_dict[unitkey] = dict()
        player_kill_count = killcounts[player] if killcounts[player] != 0 else 1 # Prevent division by zero

        for unit in sorted_dict:
            if (sorted_dict[unit][2]/player_kill_count > percent_cutoff):
                replay_report_dict[unitkey][unit] = sorted_dict[unit]
                replay_report_dict[unitkey][unit][3] = round(replay_report_dict[unitkey][unit][2]/player_kill_count,2)

                # Copy created & lost stats from Dehaka
                if unit == 'Zweihaka' and 'Dehaka' in sorted_dict:
                    replay_report_dict[unitkey][unit][0] = replay_report_dict[unitkey]['Dehaka'][0]
                    replay_report_dict[unitkey][unit][1] = replay_report_dict[unitkey]['Dehaka'][1]

                if unit in dont_show_created_lost:
                    replay_report_dict[unitkey][unit][0] = '-'
                    replay_report_dict[unitkey][unit][1] = '-'

            # Icons: Created units
            if unit in icon_units:
                replay_report_dict[iconkey][unit] = sorted_dict[unit][0]

        # Icons: Artifacts and used projections
        Zeratul_artifacts_collected = 0
        for unit in pdict:
            if unit in ['ZeratulArtifactPickup1','ZeratulArtifactPickup2','ZeratulArtifactPickup3','ZeratulArtifactPickupUnlimited']:
                Zeratul_artifacts_collected += pdict[unit][1]

            if unit in ['ZeratulKhaydarinMonolithProjection','ZeratulPhotonCannonProjection']:
                if 'ShadeProjection' in replay_report_dict[iconkey]:
                    replay_report_dict[iconkey]['ShadeProjection'] += pdict[unit][0]
                else:
                    replay_report_dict[iconkey]['ShadeProjection'] = pdict[unit][0]

        if Zeratul_artifacts_collected > 0:
            replay_report_dict[iconkey]['Artifact'] = Zeratul_artifacts_collected


    fill_unit_kills_and_icons(replay_report_dict['main'], main_player, unit_type_dict_main)
    fill_unit_kills_and_icons(replay_report_dict['ally'], ally_player, unit_type_dict_ally)

    # Icons: Killbots
    if killbot_feed[main_player] > 0:
        replay_report_dict['mainIcons']['killbots'] = killbot_feed[main_player]
    if killbot_feed[ally_player] > 0:
        replay_report_dict['allyIcons']['killbots'] = killbot_feed[ally_player]

    # Amon kills
    sorted_amon = switch_names(unit_type_dict_amon)
    sorted_amon = {k:v for k,v in sorted(sorted_amon.items(), reverse = True, key=lambda item: item[1][0])}
    sorted_amon = {k:v for k,v in sorted(sorted_amon.items(), reverse = True, key=lambda item: item[1][2])}

    # Get total amount of kills from Amon
    total_amon_kills = 0
    for player in amon_players:
        total_amon_kills += killcounts[player]
    total_amon_kills = total_amon_kills if total_amon_kills != 0 else 1

    # Calculate Amon unit percentages and fill data
    replay_report_dict['amonUnits'] = dict()

    for unit in sorted_amon:
        if not contains_skip_strings(unit) and sorted_amon[unit][2] > 0:
            replay_report_dict['amonUnits'][unit] = sorted_amon[unit]
            replay_report_dict['amonUnits'][unit][3] = round(replay_report_dict['amonUnits'][unit][2]/total_amon_kills,2)

    return replay_report_dict