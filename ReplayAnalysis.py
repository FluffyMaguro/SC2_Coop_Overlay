import os
import sys
import mpyq
import json
import traceback

import sc2reader
from FluffyChatBotDictionaries import UnitNameDict, CommanderMastery, UnitAddKillsTo
from MLogging import logclass

amon_forces = ['Amon','Infested','Salamander','Void Shard','Hologram','Moebius', "Ji'nara","Warp Conduit "]
duplicating_units = ['HotSRaptor']
skip_strings = ['placement', 'placeholder', 'dummy','cocoon','droppod',"colonist hut","bio-dome","amon's train","Warp Conduit"]
revival_types = {'KerriganReviveCocoon':'K5Kerrigan', 'AlarakReviveBeacon':'AlarakCoop','ZagaraReviveCocoon':'ZagaraVoidCoop','DehakaCoopReviveCocoonFootPrint':'DehakaCoop','NovaReviveBeacon':'NovaCoop','ZeratulCoopReviveBeacon':'ZeratulCoop'}


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



def analyse_replay(filepath, playernames=['']):
    """ Analyses the replay and returns message into the chat"""
    
    ### Structure: {unitType : [#created, #died, #kills, #killfraction]}
    unit_type_dict_main = {}
    unit_type_dict_ally = {}
    unit_type_dict_amon = {}
    logger.info(f'Analysing: {filepath}')

    ### Load the replay
    archive = mpyq.MPQArchive(filepath)
    metadata = json.loads(archive.read_file('replay.gamemetadata.json'))
    logger.debug(f'Metadata: {metadata}')


    try:
        replay = sc2reader.load_replay(filepath,load_level=3)
    except:
        logger.error(f'ERROR: sc2reader failed to load replay ({filepath})')
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
                if playeriter.lower() in str(replay.person[per]).lower() and per < 3: 
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

    logger.debug(f'Main player: {main_player_name} | {main_player} | Ally player: {ally_player_name} | {ally_player} | {amon_players}')


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
    killcounts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    ### Go through game events
    for event in replay.events:  
        if event.name == 'UnitBornEvent' or event.name == 'UnitInitEvent':
            
            unit_type = event.unit_type_name
            unit_dict[str(event.unit_id)] = [unit_type, event.control_pid]
            
            #certain hero units don't die, instead lets track their revival beacons/cocoons. Let's assume they will finish reviving.
            if unit_type in revival_types and event.control_pid in [1,2] and event.second > 0:
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
                            unit_type_dict_main[unit_type] = [1,0,0,0]

                        if ally_player == event.control_pid and not(unit_type in unit_type_dict_ally):
                            unit_type_dict_ally[unit_type] = [1,0,0,0]

                        if event.control_pid in amon_players and not(unit_type in unit_type_dict_amon):
                            unit_type_dict_amon[unit_type] = [1,0,0,0]


        #update ownership
        if event.name == 'UnitOwnerChangeEvent' and str(event.unit_id) in unit_dict:
            unit_dict[str(event.unit_id)][1] = str(event.control_pid)


        #count kills for players
        if event.name == 'UnitDiedEvent':
            try:
                losing_player = int(unit_dict[str(event.unit_id)][1])
                if losing_player != event.killing_player_id and not(event.killing_player_id in [1,2] and losing_player in [1,2]): #don't count team kills
                    killcounts[event.killing_player_id] += 1
            except:
                pass

        if event.name == 'UnitDiedEvent' and str(event.unit_id) in unit_dict:    
            try:
                killing_unit_id = str(event.killing_unit_id)
                killed_unit_type = unit_dict[str(event.unit_id)][0]
                losing_player = int(unit_dict[str(event.unit_id)][1])

                if killing_unit_id in unit_dict:
                    killing_unit_type = unit_dict[killing_unit_id][0]
                else:
                    killing_unit_type = 'NoUnit'
           
                ### Update kills
                if (killing_unit_id in unit_dict) and (killing_unit_id != str(event.unit_id)) and losing_player != event.killing_player_id:
                  
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

                #fix for raptors that are counted each time they jump (as death and birth)
                if main_player == losing_player and event.second > 0 and killed_unit_type in duplicating_units and killed_unit_type == killing_unit_type and losing_player == event.killing_player_id:
                    unit_type_dict_main[killed_unit_type][0] -= 1
                    continue

                if ally_player == losing_player and event.second > 0 and killed_unit_type in duplicating_units and killed_unit_type == killing_unit_type and losing_player == event.killing_player_id:
                    unit_type_dict_ally[killed_unit_type][0] -= 1
                    continue

                # in case of death caused by Archon merge, ignore these kills
                if (killed_unit_type == 'HighTemplar' or killed_unit_type == 'DarkTemplar') and DT_HT_Ignore[losing_player] > 0:
                    DT_HT_Ignore[losing_player] -= 1
                    continue

                if main_player == losing_player and event.second > 0: #don't count deaths on game init
                    if killed_unit_type in unit_type_dict_main:
                        unit_type_dict_main[killed_unit_type][1] += 1
                    else:
                        unit_type_dict_main[killed_unit_type] = [1,1,0,0]

                if ally_player == losing_player and event.second > 0: #don't count deaths on game init
                    if killed_unit_type in unit_type_dict_ally:
                        unit_type_dict_ally[killed_unit_type][1] += 1
                    else:
                        unit_type_dict_ally[killed_unit_type] = [1,1,0,0]

                if losing_player in amon_players and event.second > 0:
                    if killed_unit_type in unit_type_dict_amon:
                        unit_type_dict_amon[killed_unit_type][1] += 1  
                    else:
                        unit_type_dict_amon[killing_unit_type] = [1,1,0,0]  
                               
            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')

    logger.debug(f'Unit type dict main: {unit_type_dict_main}')
    logger.debug(f'Unit type dict ally: {unit_type_dict_ally}')
    logger.debug(f'Kill counts: {killcounts}')

    #Get messages
    total_kills = killcounts[1] + killcounts[2]
    replay_report = ""

    replay_report_dict = dict()
    replay_report_dict['replaydata'] = True
    replay_report_dict['result'] = game_result
    replay_report_dict['map'] = replay.map_name
    replay_report_dict['main'] = main_player_name
    replay_report_dict['mainAPM'] = map_data[main_player]
    replay_report_dict['mainkills'] = killcounts[main_player]
    replay_report_dict['ally'] = ally_player_name

    replay_report_dict['B+'] = replay.raw_data['replay.initData']['lobby_state']['slots'][0]['brutal_plus_difficulty']

    replay_report_dict['mainCommander'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander'].decode()
    replay_report_dict['mainCommanderLevel'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander_level']
    replay_report_dict['mainMasteries'] = replay.raw_data['replay.initData']['lobby_state']['slots'][main_player-1]['commander_mastery_talents']

    replay_report_dict['allyAPM'] = 0
    replay_report_dict['allykills'] = killcounts[ally_player]
    if len(replay.humans) > 1:
        replay_report_dict['allyAPM'] = map_data[ally_player]
        replay_report_dict['allyCommander'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander'].decode()
        replay_report_dict['allyCommanderLevel'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander_level']
        replay_report_dict['allyMasteries'] = replay.raw_data['replay.initData']['lobby_state']['slots'][ally_player-1]['commander_mastery_talents']
    else:
        logger.error('No ally player')

    if total_kills == 0:
        return {}

    percent_cutoff = 0.00
    player_max_units = 100 #max units sent. Javascript then sets its own limit.

    def playercalc(playername,player,pdict):
        new_dict = switch_names(pdict)
        sorted_dict = {k:v for k,v in sorted(new_dict.items(), reverse = True, key=lambda item: item[1][2])} #sorts by number of create (0), lost (1), kills (2), K/D (3)
        message_count = 0

        #save data
        unitkey = 'mainUnits' if player == main_player else 'allyUnits'
        replay_report_dict[unitkey] = dict()
        player_kill_count = killcounts[player] if killcounts[player] != 0 else 1 #prevent zero division
        idx = 0
        for unit in sorted_dict:
            idx += 1
            if (sorted_dict[unit][2]/player_kill_count > percent_cutoff) and idx < (player_max_units+1):
                replay_report_dict[unitkey][unit] = sorted_dict[unit]
                replay_report_dict[unitkey][unit][3] = round(replay_report_dict[unitkey][unit][2]/player_kill_count,2)


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

    file_path = 'VP.SC2Replay'
    replay_dict = analyse_replay(file_path,['Maguro'])
    pprint(replay_dict, sort_dicts=False)

    