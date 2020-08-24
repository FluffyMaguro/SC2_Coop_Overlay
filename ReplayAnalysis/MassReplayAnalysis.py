"""
This module is used for generating overall stats from a list of replays (and main names)

TODO:
- decide how to store already parsed data so we don't have to do it all the time again (likely store as json and check against a set of replay file_paths)
- create a function for mass parse and replay store (instead of main), IN: replay paths, names | OUT: dictionary with all computed
- incorporate it into the app

"""

import os
import time
import traceback
import statistics 

from ReplayAnalysis.S2Parser import s2_parse_replay


AllReplays = set()
MainNames = set()




############ DEBUG ###########

for root, directories, files in os.walk(r'C:\Users\Maguro\Documents\StarCraft II\Accounts'):
    for file in files:
        if file.endswith('.SC2Replay'):
            file_path = os.path.join(root,file)
            if len(file_path) > 255:
                file_path = '\\\?\\' + file_path
            file_path = file_path = os.path.normpath(file_path)
            AllReplays.add(file_path)

MainNames = {'Maguro','Potato','SeaMaguro','BigMaguro'}

##############################


def parse_replay(file):
    """ Parse replay with added exceptions and set key-arguments """
    try:
        return s2_parse_replay(file, try_lastest=False, parse_events=False, onlyBlizzard=True, withoutRecoverEnabled=True)
    except:
        print(file,traceback.format_exc())
        return None


def calculate_difficulty_data(ReplayData):
    """ Calculates the number of wins and losses for each difficulty"""
    DifficultyData = dict()

    for r in ReplayData:
        diff = r['ext_difficulty']
        # Skip mixed difficulties
        if '/' in diff:
            continue
        # Add empty dict
        if not diff in DifficultyData:
            DifficultyData[diff] = {'Victory':0,'Defeat':0}

        DifficultyData[diff][r['result']] += 1

    return DifficultyData


def calculate_map_data(ReplayData):
    """ Calculates the number of wins and losses for each map """
    MapData = dict()

    for r in ReplayData:
        if not r['map_name'] in MapData:
            MapData[r['map_name']] = {'Victory':0,'Defeat':0,'Fastest':{'length':99999999}}

        MapData[r['map_name']][r['result']] += 1
        # Fastest clears
        if r['result'] == 'Victory' and r['accurate_length'] < MapData[r['map_name']]['Fastest']['length'] and r['difficulty'][0] == 'Brutal' and r['difficulty'][1] == 'Brutal':
            MapData[r['map_name']]['Fastest']['length'] = r['accurate_length']
            MapData[r['map_name']]['Fastest']['file'] = r['file']
            MapData[r['map_name']]['Fastest']['players'] = r['players'][1:3]
            MapData[r['map_name']]['Fastest']['enemy_race'] = r['enemy_race']

    return MapData


def calculate_commander_data(ReplayData, MainNames):
    """ Calculates the number of wins and losses for each commander
    Returns separate objects for players in MainNames (capitalization not important) and those that are not"""
    CommanderData = dict()
    AllyCommanderData = dict()
    MainNames = {n.lower() for n in MainNames}
    games = 0

    for r in ReplayData:
        for p in {1,2}:
            commander = r['players'][p]['commander']
            if r['players'][p]['name'].lower() in MainNames:
                if not commander in CommanderData:
                    CommanderData[commander] = {'Victory':0,'Defeat':0}

                CommanderData[commander][r['result']] += 1
                games += 1
            else:
                if not commander in AllyCommanderData:
                    AllyCommanderData[commander] = {'Victory':0,'Defeat':0,'MedianAPM':list(),'Prestige':list(),'Mastery':list()}

                AllyCommanderData[commander][r['result']] += 1
                AllyCommanderData[commander]['MedianAPM'].append(r['players'][p]['apm'])
                AllyCommanderData[commander]['Prestige'].append(r['players'][p]['prestige'])

                # Add masteries, use relative values to properly reflect player preferences
                masteries = r['players'][p]['masteries']
                mastery_sum = sum(masteries)/3
                masteries = [m/mastery_sum for m in masteries] if mastery_sum != 0 else masteries
                AllyCommanderData[commander]['Mastery'].append(masteries)


    # Main player            
    for commander in CommanderData:
        CommanderData[commander]['Frequency'] = (CommanderData[commander]['Victory'] + CommanderData[commander]['Defeat'])/games
        CommanderData[commander]['Winrate'] = CommanderData[commander]['Victory']/games
        
    # Ally
    would_be_observed_games_total = 0
    for commander in AllyCommanderData:
        # Winrate
        AllyCommanderData[commander]['Winrate'] = AllyCommanderData[commander]['Victory']/(AllyCommanderData[commander]['Victory'] + AllyCommanderData[commander]['Defeat'])

        # APM
        AllyCommanderData[commander]['MedianAPM'] = statistics.median(AllyCommanderData[commander]['MedianAPM'])

        # Mastery (sum list of lists, normalize)
        mastery_summed = {0:0,1:0,2:0,3:0,4:0,5:0}
        for i in AllyCommanderData[commander]['Mastery']:
            for idx,m in enumerate(i):
                mastery_summed[idx] += m

        # Normalize mastery choices
        mastery_summed_copy = mastery_summed.copy()
        for idx,m in enumerate(mastery_summed):
            mastery_summed[idx] = mastery_summed[idx]/(mastery_summed_copy[(idx//2)*2]+mastery_summed_copy[(idx//2)*2+1])

        AllyCommanderData[commander]['Mastery'] = mastery_summed

        # Prestige
        AllyCommanderData[commander]['Prestige'] = {i:AllyCommanderData[commander]['Prestige'].count(i)/len(AllyCommanderData[commander]['Prestige']) for i in {0,1,2,3}}

        # For ally correct frequency for the main player selecting certain commander (1/(1-f)) factor and rescale
        would_be_observed_games = (1/(1-CommanderData[commander]['Frequency']))*(AllyCommanderData[commander]['Victory']+AllyCommanderData[commander]['Defeat'])
        AllyCommanderData[commander]['Frequency'] = would_be_observed_games
        would_be_observed_games_total += would_be_observed_games

    for commander in AllyCommanderData:
        AllyCommanderData[commander]['Frequency'] = AllyCommanderData[commander]['Frequency']/would_be_observed_games_total

    return CommanderData, AllyCommanderData



def main():
    import pickle
    from pprint import pprint
    if False:
        ts = time.time()
        ReplayData = map(parse_replay, AllReplays)

        ReplayData = [r for r in ReplayData if r != None]
        print(f'Successfully parsed {len(ReplayData)}/{len(AllReplays)} in {time.time()-ts:.1f} seconds')

        
        with open('ReplayData','wb') as f:
            pickle.dump(ReplayData, f, protocol=5)
    else:
        with open('ReplayData','rb') as f:
            ReplayData = pickle.load(f)

    # from pprint import pprint 
    # pprint(ReplayData)

    # import json
    # with open('ReplayData.json', 'w') as f:
    #     json.dump(ReplayData, f, indent=2)


    # 4352/5024 | 44.3s - base
    # 4352/5024 | 43.9 - no recovery
    # 4328/5024 | 42.1 - no lastest version
    # 4352/5024 | 44.7 - with MM excluded straight away    
    # 4328/5024 | 41.2 - no lastest
    # 4328/5024 | 4185 - with parsing events

    # Exclude weekly/custom
    ReplayData = [r for r in ReplayData if r['extension'] == False]

    # Get difficulty data
    DifficultyData = calculate_difficulty_data(ReplayData)
    # pprint(DifficultyData)

    # # Get map data
    MapData = calculate_map_data(ReplayData)
    pprint(MapData)

    # # Get main commander data
    CommanderData, AllyCommanderData = calculate_commander_data(ReplayData, MainNames)
    # pprint(CommanderData)

    pprint(AllyCommanderData)






