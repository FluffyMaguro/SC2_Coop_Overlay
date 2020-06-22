import os
import mpyq
import json
import time
import traceback

from s2protocol import versions
import sc2reader
from FluffyChatBotDictionaries import UnitNameDict, CommanderMastery, UnitAddKillsTo, UnitCompDict, UnitsInWaves, COMasteryUpgrades
from MLogging import logclass

amon_forces = ['Amon','Infested','Salamander','Void Shard','Hologram','Moebius', "Ji'nara","Warp Conduit "]
duplicating_units = ['HotSRaptor','MutatorAmonArtanis','HellbatBlackOps']
skip_strings = ['placement', 'placeholder', 'dummy','cocoon','droppod',"colonist hut","bio-dome","amon's train","warp conduit"]
revival_types = {'KerriganReviveCocoon':'K5Kerrigan', 'AlarakReviveBeacon':'AlarakCoop','ZagaraReviveCocoon':'ZagaraVoidCoop','DehakaCoopReviveCocoonFootPrint':'DehakaCoop','NovaReviveBeacon':'NovaCoop','ZeratulCoopReviveBeacon':'ZeratulCoop'}
icon_units = {'MULE','Omega Worm'}
self_killing_units = {'FenixCoop', 'FenixDragoon', 'FenixArbiter'}
dont_show_created_lost = {'Tychus Findlay',"James 'Sirius' Sykes","Kev 'Rattlesnake' West",'Nux','Crooked Sam','Lt. Layna Nikara',"Miles 'Blaze' Lewis","Rob 'Cannonball' Boswell","Vega"}
aoe_units = {'Raven','ScienceVessel','Viper','HybridDominator','Infestor','HighTemplar','Blightbringer','TitanMechAssault','MutatorAmonNova'}
tychus_outlaws = {'TychusCoop','TychusReaper','TychusWarhound','TychusMarauder','TychusHERC','TychusFirebat','TychusGhost','TychusSpectre','TychusMedic',}
commander_upgrades = { "AlarakCommander":"Alarak", "ArtanisCommander":"Artanis", "FenixCommander":"Fenix", "KaraxCommander":"Karax", "VorazunCommander":"Vorazun", "ZeratulCommander":"Zeratul", "HornerCommander":"Han & Horner", "MengskCommander":"Mengsk", "NovaCommander":"Nova", "RaynorCommander":"Raynor", "SwannCommander":"Swann", "TychusCommander":"Tychus", "AbathurCommander":"Abathur", "DehakaCommander":"Dehaka", "KerriganCommander":"Kerrigan", "StukovCommander":"Stukov", "ZagaraCommander":"Zagara", "StetmannCommander":"Stetmann"}

logger = logclass('REPA','INFO')


def contains_skip_strings(pname):
    """ checks if any of skip strings is in the pname """
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
    """ the function checks if the upgrade is in mastery upgrades, and if yes, returns the Commnader and upgrade index"""
    for co in COMasteryUpgrades:
        if upgrade in COMasteryUpgrades[co]:
            return co, COMasteryUpgrades[co].index(upgrade)
    return False, 0
               

def switch_names(pdict):
    """ Changes names to that in unit dictionary, sums duplicates"""
    temp_dict = {}

    for key in pdict:
        #for locusts, broodlings, interceptors, add kills to the main unit. Don't add unit created/lost
        if key in UnitAddKillsTo:
            name = UnitAddKillsTo[key]
            if name in temp_dict:
                temp_dict[name][2] += pdict[key][2]
            else:
                temp_dict[name] = [0,0,pdict[key][2],0]

        else:
            #translate names & sum up those with the same names
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
    """ this function takes indentified waves and tries to match them with known enemy AI comps.
        Waves are identified as events where 6+ units were created at the same second. """

    #each AI gets one point for each matching wave
    results = dict()
    for AI in UnitCompDict:
        results[AI] = 0

    #lets go through our waves, substract some units and compare them to known AI unit waves
    for wave in identified_waves:
        types = set(identified_waves[wave])
        if len(types) == 0:
            continue

        logger.debug(f'{"-"*40}\nChecking this wave type: {types}\n')
        for AI in UnitCompDict:
            for idx,wave in enumerate(UnitCompDict[AI]):
                #don't include Medivac, it's removed from wave units as well
                wave.difference_update({'Medivac'})

                #identical wave
                if types == wave:
                    logger.debug(f'"{AI}" wave {idx+1} is the same: {wave}')
                    results[AI] += 1*len(wave)
                    continue

                #in case of alternate units or some noise
                if types.issubset(wave) and len(wave) - len(types) == 1: 
                    logger.debug(f'"{AI}" wave {idx+1} is a close subset: {types} | {wave}')
                    results[AI] += 0.25*len(wave)

    results = {k:v for k,v in sorted(results.items(), key=lambda x:x[1],reverse=True) if v!=0}            
    logger.debug(f'{"-"*40}\nAnd results are: {results}')

    #return the comp with the most points
    if len(results) > 0:
        logger.debug(f'Most likely AI: "{list(results.keys())[0]}" with {100*list(results.values())[0]/sum(results.values()):.1f}% points\n\n')
        return list(results.keys())[0]
    return 'unidentified AI'


def get_last_deselect_event(file,archive=None):
    """ this functions gets time of the last deselect event in the replay"""
    if archive == None:
        archive = mpyq.MPQArchive(file) #passing already opened archive inside 

    contents = archive.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)
    base_build = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(base_build)
    except:
        protocol = protocol = versions.latest()

    game_events = archive.read_file('replay.game.events')
    game_events = protocol.decode_replay_game_events(game_events)
    """
    'SSelectionDeltaEvent', 'SCameraSaveEvent', 'STriggerCutsceneEndSceneFiredEvent', 'STriggerDialogControlEvent', 'SSetSyncLoadingTimeEvent', 
    'SCmdEvent', 'SUserFinishedLoadingSyncEvent', 'STriggerSoundLengthSyncEvent', 'STriggerSoundOffsetEvent', 'SControlGroupUpdateEvent', 
    'STriggerTransmissionCompleteEvent', 'SUserOptionsEvent', 'SCommandManagerStateEvent', 'SGameUserLeaveEvent', 'SCmdUpdateTargetPointEvent', 
    'SAchievementAwardedEvent', 'SCmdUpdateTargetUnitEvent', 'STriggerTransmissionOffsetEvent', 'SCameraUpdateEvent', 'SSetSyncPlayingTimeEvent', 
    'STriggerCutsceneBookmarkFiredEvent', 'STriggerSoundLengthQueryEvent'"""
    

    # tracker_events = archive.read_file('replay.tracker.events')
    # tracker_events = protocol.decode_replay_tracker_events(tracker_events) 
    """ 
    SUnitPositionsEvent', 'SUnitDiedEvent', 'SUpgradeEvent', 'SUnitInitEvent', 'SPlayerStatsEvent', 'SUnitDoneEvent', 'SUnitTypeChangeEvent', 
    'SPlayerSetupEvent', 'SUnitOwnerChangeEvent', 'SUnitBornEvent'
    """

    # player_info = archive.read_file('replay.details')
    # player_info = protocol.decode_replay_details(player_info)
    # detailed_info = archive.read_file('replay.initData')
    # detailed_info = protocol.decode_replay_initdata(detailed_info)

    last_event = 0
    for event in list(game_events):
        if event['_event'] == 'NNet.Game.SSelectionDeltaEvent':
            last_event = event['_gameloop']/16 - 2 #16 gameloops per second, offset to coincide with speedrun timings more

    return last_event


def analyse_replay(filepath, playernames=['']):
    """ Analyses the replay and returns message into the chat"""
    
    ### Structure: {unitType : [#created, #died, #kills, #killfraction]}
    unit_type_dict_main = {}
    unit_type_dict_ally = {}
    unit_type_dict_amon = {}
    logger.info(f'Analysing: {filepath}')

    ### Load the replay
    for i in range(4):
        try:
            archive = mpyq.MPQArchive(filepath)
            metadata = json.loads(archive.read_file('replay.gamemetadata.json'))
            logger.debug(f'Metadata: {metadata}')
            break
        except:  #I got an error here once that went away the second time I tried it. Perhaps SC2 didn't finish writing in the file? 
            logger.error('Error parsing with mpyq ')
            time.sleep(0.5)


    try:
        replay = sc2reader.load_replay(filepath,load_level=3)
    except:
        logger.error(f'ERROR: sc2reader failed to load replay ({filepath})\n{traceback.format_exc()}')
        return {}

    
    ### find Amon players
    amon_players = set()
    amon_players.add(3)
    amon_players.add(4)
    for per in replay.person:
        if check_amon_forces(amon_forces,str(replay.person[per])) and per > 4:
            amon_players.add(per)


    ### Find player names and numbers
    main_player = 1
    main_player_name = ''

    #check if you can find the name in the lsit
    if len(playernames)>0:
        for per in replay.person:
            for playeriter in playernames:
                if playeriter.lower() in str(replay.person[per]).lower() and per < 3 and main_player_name == '': 
                    main_player = per
                    main_player_name = playeriter
                    break

    #in case the name wasn't found            
    if main_player_name == '':
        main_player_name = str(replay.person[main_player]).split(' - ')[1].replace(' (Zerg)', '').replace(' (Terran)', '').replace(' (Protoss)', '')
   
    #ally
    ally_player = 1 if main_player == 2 else 2
    #fix for playing alone
    if len(replay.humans) == 1:
        ally_player_name = 'None'
    else:
        ally_player_name = str(replay.person[ally_player]).split(' - ')[1].replace(' (Zerg)', '').replace(' (Terran)', '').replace(' (Protoss)', '')

    logger.debug(f'Main player: {main_player_name} | {main_player} | Ally player: {ally_player_name} | {ally_player} | Amon players: {amon_players}')


    ### get APM & Game result
    game_result = 'Defeat'
    map_data = dict()
    map_data[main_player] = 0
    map_data[ally_player] = 0

    for player in metadata["Players"]:
        if player["PlayerID"] == main_player:
            map_data[main_player] = player["APM"]
            if player["Result"] == 'Win':
                game_result = 'Victory'
        elif player["PlayerID"] == ally_player:
            map_data[ally_player] = player["APM"]
            if player["Result"] == 'Win':
                game_result = 'Victory'

    logger.debug(f'Map data: {map_data}')


    unit_dict = {} #structure: {unit_id : [UnitType, Owner]}; used to track all units
    DT_HT_Ignore = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #ignore certain amount of DT/HT deaths after archon is initialized. DT_HT_Ignore[player]
    killcounts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    START_TIME = 99999999
    commander_fallback = dict()
    outlaw_order = []
    wave_units = {'second':0,'units':[]}
    identified_waves = dict()
    mastery_fallback = {1:[0,0,0,0,0,0],2:[0,0,0,0,0,0]}

    last_aoe_unit_killed = [0]*17
    for player in range(1,16):
        last_aoe_unit_killed[player] = [None, 0] if player in amon_players else None


    ### Go through game events
    for event in replay.events:  

        #get actual start time for arcade maps/customs
        if event.name == 'PlayerStatsEvent' and event.pid == 1 and event.minerals_collection_rate > 0 and START_TIME == 99999999: 
            START_TIME = event.second 
            logger.debug(f'Mission start through player stats: {START_TIME}') #this is a fallback. Upgrade should always kick in first. 

        if event.name == 'UpgradeCompleteEvent':
            if event.name == 'UpgradeCompleteEvent' and event.pid in [1,2] and 'Spray' in event.upgrade_type_name and START_TIME == 99999999:     
                START_TIME = event.second
                logger.debug(f'Mission start through player upgrade: {START_TIME}')

            #commander fallback
            if event.pid in [1,2] and event.upgrade_type_name in commander_upgrades:
                commander_fallback[event.pid] = commander_upgrades[event.upgrade_type_name]

            #mastery upgrade fallback
            mas_commander,mas_index = upgrade_is_in_mastery_upgrades(event.upgrade_type_name)
            if mas_commander and event.pid in [1,2]:
                logger.debug(f'Player {event.pid} (com: {mas_commander}) got upgrade {event.upgrade_type_name} (idx: {mas_index}) (count: {event.count})')
                mastery_fallback[event.pid][mas_index] = event.count


        if event.name == 'UnitBornEvent' or event.name == 'UnitInitEvent':
            unit_type = event.unit_type_name
            unit_dict[str(event.unit_id)] = [unit_type, event.control_pid]

            #certain hero units don't die, instead lets track their revival beacons/cocoons. Let's assume they will finish reviving.
            if unit_type in revival_types and event.control_pid in [1,2] and event.second > START_TIME:
                if event.control_pid == main_player:
                    unit_type_dict_main[revival_types[unit_type]][1] += 1
                    unit_type_dict_main[revival_types[unit_type]][0] += 1
                if event.control_pid == ally_player:
                    unit_type_dict_ally[revival_types[unit_type]][1] += 1
                    unit_type_dict_ally[revival_types[unit_type]][0] += 1


            #save stats for units created
            if main_player == event.control_pid:
                if unit_type in unit_type_dict_main:
                    unit_type_dict_main[unit_type][0] += 1
                else:
                    unit_type_dict_main[unit_type] = [1,0,0,0]

            if ally_player == event.control_pid:
                if unit_type in unit_type_dict_ally:
                    unit_type_dict_ally[unit_type][0] += 1
                else:
                    unit_type_dict_ally[unit_type] = [1,0,0,0]

            if event.control_pid in amon_players:
                if unit_type in unit_type_dict_amon:
                    unit_type_dict_amon[unit_type][0] += 1
                else:
                    unit_type_dict_amon[unit_type] = [1,0,0,0]

            #outlaw order
            if unit_type in tychus_outlaws and event.control_pid in [1,2] and not(unit_type in outlaw_order):
                outlaw_order.append(unit_type)

            #identifying waves
            if event.control_pid in [3,4,5,6] and not event.second in [0,START_TIME] and event.second > 60 and unit_type in UnitsInWaves:
                if wave_units['second'] == event.second:
                    wave_units['units'].append(unit_type)
                else:
                    wave_units['second'] = event.second
                    wave_units['units'] = [unit_type]

                if len(wave_units['units']) > 5:
                    identified_waves[event.second] = wave_units['units']

        #ignore some DT/HT deaths caused by Archon merge
        if event.name == "UnitInitEvent" and event.unit_type_name == "Archon":
            DT_HT_Ignore[event.control_pid] += 2

        if event.name == 'UnitTypeChangeEvent' and str(event.unit_id) in unit_dict:
                #update unit_dict
                old_unit_type = unit_dict[str(event.unit_id)][0]
                unit_dict[str(event.unit_id)][0] = str(event.unit_type_name)

                #add to created units
                unit_type = event.unit_type_name
           
                if unit_type in UnitNameDict and old_unit_type in UnitNameDict:
                    event.control_pid = int(unit_dict[str(event.unit_id)][1])
                    if UnitNameDict[unit_type] != UnitNameDict[old_unit_type]: #don't add into created units if it's just a morph

                        # #increase unit type created for controlling player 
                        if main_player == event.control_pid:
                            if unit_type in unit_type_dict_main:
                                unit_type_dict_main[unit_type][0] += 1
                            else:
                                unit_type_dict_main[unit_type] = [1,0,0,0]

                        if ally_player == event.control_pid:
                            if unit_type in unit_type_dict_ally:
                                unit_type_dict_ally[unit_type][0] += 1
                            else:
                                unit_type_dict_ally[unit_type] = [1,0,0,0]

                        if event.control_pid in amon_players:
                            if unit_type in unit_type_dict_amon:
                                unit_type_dict_amon[unit_type][0] += 1
                            else:
                                unit_type_dict_amon[unit_type] = [1,0,0,0]
                    else:
                        if main_player == event.control_pid and not(unit_type in unit_type_dict_main):
                            unit_type_dict_main[unit_type] = [0,0,0,0]

                        if ally_player == event.control_pid and not(unit_type in unit_type_dict_ally):
                            unit_type_dict_ally[unit_type] = [0,0,0,0]

                        if event.control_pid in amon_players and not(unit_type in unit_type_dict_amon):
                            unit_type_dict_amon[unit_type] = [0,0,0,0]


        #update ownership
        if event.name == 'UnitOwnerChangeEvent' and str(event.unit_id) in unit_dict:
            unit_dict[str(event.unit_id)][1] = str(event.control_pid)
       
        if event.name == 'UnitDiedEvent':
            try:
                killed_unit_type = unit_dict[str(event.unit_id)][0]
                losing_player = int(unit_dict[str(event.unit_id)][1])

                #count kills for players
                if losing_player != event.killing_player_id and killed_unit_type != 'FuelCellPickupUnit' and not(event.killing_player_id in [1,2] and losing_player in [1,2]) and event.killing_player_id != None: #don't count team kills
                    killcounts[event.killing_player_id] += 1

                #get last_aoe_unit_killed
                if killed_unit_type in aoe_units and event.killing_player_id in [1,2] and losing_player in amon_players:
                    last_aoe_unit_killed[losing_player] = [killed_unit_type,event.second]

            except:
                logger.error(traceback.format_exc())


        if event.name == 'UnitDiedEvent' and str(event.unit_id) in unit_dict:    
            try:
                killing_unit_id = str(event.killing_unit_id)
                killed_unit_type = unit_dict[str(event.unit_id)][0]
                losing_player = int(unit_dict[str(event.unit_id)][1])


                if killing_unit_id in unit_dict:
                    killing_unit_type = unit_dict[killing_unit_id][0]
                else:
                    killing_unit_type = 'NoUnit'


                """Fix kills for some enemy area-of-effect units that kills player units after they are dead. 
                   This is the best guess, if one of aoe_units died recently, it was likely that one. """
                if killing_unit_type == 'NoUnit' and event.killing_unit_id == None and event.killer_pid in amon_players and losing_player != event.killing_player_id:
                    if event.second - last_aoe_unit_killed[event.killer_pid][1] < 9 and last_aoe_unit_killed[event.killer_pid][0] != None:
                        unit_type_dict_amon[last_aoe_unit_killed[event.killer_pid][0]][2] += 1
                        logger.debug(f'{last_aoe_unit_killed[event.killer_pid][0]}({event.killer_pid}) killed {killed_unit_type} | {event.second}s')


                ### Update kills
                if (killing_unit_id in unit_dict) and (killing_unit_id != str(event.unit_id)) and losing_player != event.killing_player_id and killed_unit_type != 'FuelCellPickupUnit':
                    if main_player == event.killing_player_id:
                        if killing_unit_type in unit_type_dict_main:
                            unit_type_dict_main[killing_unit_type][2] += 1
                        else:
                            unit_type_dict_main[killing_unit_type] = [0,0,1,0]

                    if ally_player == event.killing_player_id:
                        if killing_unit_type in unit_type_dict_ally:
                            unit_type_dict_ally[killing_unit_type][2] += 1
                        else:
                            unit_type_dict_ally[killing_unit_type] = [0,0,1,0]

                    if event.killing_player_id in amon_players:  
                        if killing_unit_type in unit_type_dict_amon:
                            unit_type_dict_amon[killing_unit_type][2] += 1
                        else:
                            unit_type_dict_amon[killing_unit_type] = [0,0,1,0]

               
                ### Update unit deaths

                # Don't count self kills like Fenix switching suits
                if killed_unit_type in self_killing_units and event.killer == None:
                    if main_player == losing_player:
                        unit_type_dict_main[killed_unit_type][0] -= 1
                    if ally_player == losing_player:
                        unit_type_dict_ally[killed_unit_type][0] -= 1
                    continue


                # Fix for raptors that are counted each time they jump (as death and birth)
                if event.second > 0 and killed_unit_type in duplicating_units and killed_unit_type == killing_unit_type and losing_player == event.killing_player_id:
                    if main_player == losing_player:
                        unit_type_dict_main[killed_unit_type][0] -= 1
                        continue
                    if ally_player == losing_player:
                        unit_type_dict_ally[killed_unit_type][0] -= 1
                        continue
                    if event.killing_player_id in amon_players:
                        unit_type_dict_amon[killed_unit_type][0] -= 1
                        continue
                   
                    
                # In case of death caused by Archon merge, ignore these kills
                if (killed_unit_type == 'HighTemplar' or killed_unit_type == 'DarkTemplar') and DT_HT_Ignore[losing_player] > 0:
                    DT_HT_Ignore[losing_player] -= 1
                    continue

                # Add deaths
                if main_player == losing_player and event.second > 0 and event.second > START_TIME: #don't count deaths on game init
                    if killed_unit_type in unit_type_dict_main:
                        unit_type_dict_main[killed_unit_type][1] += 1
                    else:
                        unit_type_dict_main[killed_unit_type] = [0,1,0,0]

                if ally_player == losing_player and event.second > 0 and event.second > START_TIME: #don't count deaths on game init
                    if killed_unit_type in unit_type_dict_ally:
                        unit_type_dict_ally[killed_unit_type][1] += 1
                    else:
                        unit_type_dict_ally[killed_unit_type] = [0,1,0,0]

                if losing_player in amon_players and event.second > 0 and event.second > START_TIME:
                    if killed_unit_type in unit_type_dict_amon:
                        unit_type_dict_amon[killed_unit_type][1] += 1  
                    else:
                        unit_type_dict_amon[killing_unit_type] = [0,1,0,0]  
                               
            except:
                logger.error(traceback.format_exc())

    if START_TIME > 6000:
        logger.error('Failed to detect the start of the game')


    logger.debug(f'Unit type dict main: {unit_type_dict_main}')
    logger.debug(f'Unit type dict ally: {unit_type_dict_ally}')
    logger.debug(f'Unit type dict amon: {unit_type_dict_amon}')
    logger.debug(f'Kill counts: {killcounts}')


    #Get messages
    total_kills = killcounts[1] + killcounts[2]
    replay_report = ""

    replay_report_dict = dict()
    replay_report_dict['replaydata'] = True
    replay_report_dict['comp'] = get_enemy_comp(identified_waves)
    replay_report_dict['result'] = game_result
    replay_report_dict['map'] = replay.map_name
    replay_report_dict['filepath'] = filepath
    replay_report_dict['date'] = str(replay.date)

    accurate_game_length = get_last_deselect_event(filepath,archive=archive)/1.4
    replay_report_dict['length'] = accurate_game_length if accurate_game_length > 0 else replay.game_length.seconds
    replay_report_dict['main'] = main_player_name
    replay_report_dict['mainAPM'] = map_data[main_player]
    replay_report_dict['mainkills'] = killcounts[main_player]
    replay_report_dict['ally'] = ally_player_name
    replay_report_dict['extension'] = replay.raw_data['replay.initData']['game_description']['has_extension_mod']

    replay_report_dict['mainIcons'] = dict()
    replay_report_dict['allyIcons'] = dict()

    replay_report_dict['B+'] = replay.raw_data['replay.initData']['lobby_state']['slots'][0]['brutal_plus_difficulty']

    replay_report_dict['mainCommander'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander'].decode()
    if replay_report_dict['mainCommander'] == '':
        replay_report_dict['mainCommander'] = commander_fallback.get(main_player,"")

    replay_report_dict['mainCommanderLevel'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander_level']
    replay_report_dict['mainMasteries'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander_mastery_talents']

    replay_report_dict['allyAPM'] = 0
    replay_report_dict['allykills'] = killcounts[ally_player]
    if len(replay.humans) > 1:
        replay_report_dict['allyAPM'] = map_data[ally_player]
        replay_report_dict['allyCommander'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander'].decode()
        if replay_report_dict['allyCommander'] == '':
            replay_report_dict['allyCommander'] = commander_fallback.get(ally_player,"")

        replay_report_dict['allyCommanderLevel'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander_level']
        replay_report_dict['allyMasteries'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander_mastery_talents']
    else:
        logger.debug('No ally player')

    if '[MM]' in filepath:
        replay_report_dict['mainMasteries'] = mastery_fallback[main_player]
        replay_report_dict['allyMasteries'] = mastery_fallback[ally_player]

    if replay_report_dict.get('mainCommander',None) == 'Tychus':
        replay_report_dict['mainIcons']['outlaws'] = outlaw_order
    elif replay_report_dict.get('allyCommander',None) == 'Tychus':
        replay_report_dict['allyIcons']['outlaws'] = outlaw_order

    percent_cutoff = 0.00
    player_max_units = 100 #max units sent. Javascript then sets its own limit.


    def playercalc(playername,player,pdict):
        new_dict = switch_names(pdict)
        sorted_dict = {k:v for k,v in sorted(new_dict.items(), reverse = True, key=lambda item: item[1][2])} #sorts by number of create (0), lost (1), kills (2), K/D (3)
        message_count = 0

        #save data
        unitkey = 'mainUnits' if player == main_player else 'allyUnits'
        iconkey = 'mainIcons' if player == main_player else 'allyIcons'
        replay_report_dict[unitkey] = dict()
        player_kill_count = killcounts[player] if killcounts[player] != 0 else 1 #prevent zero division
        idx = 0
        for unit in sorted_dict:
            idx += 1
            if (sorted_dict[unit][2]/player_kill_count > percent_cutoff) and idx < (player_max_units+1):
                replay_report_dict[unitkey][unit] = sorted_dict[unit]
                replay_report_dict[unitkey][unit][3] = round(replay_report_dict[unitkey][unit][2]/player_kill_count,2)

                if unit in dont_show_created_lost:
                    replay_report_dict[unitkey][unit][0] = 'N/A'
                    replay_report_dict[unitkey][unit][1] = 'N/A'

            #icons        
            if unit in icon_units:
                replay_report_dict[iconkey][unit] = sorted_dict[unit][0]

        for unit in pdict:
            #save the number of shade projections into icons
            if unit in ['ZeratulKhaydarinMonolithProjection','ZeratulPhotonCannonProjection']:
                if 'ShadeProjection' in replay_report_dict[iconkey]:
                    replay_report_dict[iconkey]['ShadeProjection'] += pdict[unit][0]
                else:
                    replay_report_dict[iconkey]['ShadeProjection'] = pdict[unit][0]



    playercalc(main_player_name, main_player, unit_type_dict_main)
    playercalc(ally_player_name, ally_player, unit_type_dict_ally)


    #Amon kills
    message_count = 0
    sorted_amon = switch_names(unit_type_dict_amon)
    sorted_amon = {k:v for k,v in sorted(sorted_amon.items(), reverse = True, key=lambda item: item[1][0])}
    sorted_amon = {k:v for k,v in sorted(sorted_amon.items(), reverse = True, key=lambda item: item[1][2])}

    # get total amount of kills from Amon
    total_amon_kills = 0
    for player in amon_players:
        total_amon_kills += killcounts[player]
    total_amon_kills = total_amon_kills if total_amon_kills != 0 else 1

    #calculate Amon unit percentages and fill data
    replay_report_dict['amonUnits'] = dict()
    idx = 0
    for unit in sorted_amon:
        idx += 1
        if (contains_skip_strings(unit)==False) and idx < (player_max_units+1) and sorted_amon[unit][2] > 0:
            replay_report_dict['amonUnits'][unit] = sorted_amon[unit]
            replay_report_dict['amonUnits'][unit][3] = round(replay_report_dict['amonUnits'][unit][2]/total_amon_kills,2)


    return replay_report_dict


### FOR DEBUGGING PURPOSES
if __name__ == "__main__":
    from pprint import pprint

    file_path = r'C:\Users\Maguro\Documents\StarCraft II\Accounts\452875987\2-S2-1-7503439\Replays\Multiplayer\Malwarfare (21).SC2Replay'
    replay_dict = analyse_replay(file_path,['Maguro'])
    # pprint(replay_dict, sort_dicts=False)
