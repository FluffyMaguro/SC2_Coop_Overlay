"""
This module is used for generating overall stats from a list/set of replays

"""

import os
import time
import traceback

from S2Parser import s2_parse_replay


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
    """ Parse replay with added exceptions """
    try:
        return s2_parse_replay(file, try_lastest=False, parse_events=False, onlyBlizzard=True, withoutRecoverEnabled=True)
    except:
        print(file,traceback.format_exc())
        return None


def difficulty(replay):
    """ Returns the difficulty including B+ games

    !!!MAYBE merge this into the parser as replay['ext_difficulty'] """

    if replay['brutal_plus'] > 0:
        return f'B+{replay["brutal_plus"][0]}'
    else:
        return replay['difficulty'][0]


def calculate_difficulty_data(ReplayData):
    """ Calculates the number of wins and losses for each difficulty"""

    DifficultyData = dict()

    for r in ReplayData:
        diff = difficulty(r)
        if not diff in DifficultyData:
            DifficultyData[diff] = {'Victory':0,'Defeat':0}

        DifficultyData[diff][r['result']] += 1

    return DifficultyData


def calculate_map_data(ReplayData):
    """ Calculates the number of wins and losses for each map

    !!! SOMEHOW GET THE ENGLISH NAME OF THE MAP"""
    MapData = dict()

    for r in ReplayData:
        if not r['map'] in MapData:
            MapData[r['map']] = {'Victory':0,'Defeat':0}

        MapData[r['map']][r['result']] += 1

    return MapData


def calculate_commander_data(ReplayData, MainNames):
    """ Calculates the number ofwins and losses for each commander
    Only does so for players in MainNames (capitalization not important)"""
    CommanderData = dict()
    MainNames = {n.lower() for n in MainNames}

    for r in ReplayData:
        for p in {1,2}:
            if ReplayData['players'][p]['name'].lower() in MainNames:
                commander =  ReplayData['players'][p]['commander']
                if not commander in CommanderData:
                    CommanderData['commander'] = {'Victory':0,'Defeat':0}

                CommanderData['commander'][r['result']] += 1

    return CommanderData


def calculate_ally_commander_data(ReplayData, MainNames):
    """ Calculates data for ally commander pick
    Frequencies are corrected for the main player commander choices """

    AllyCommanderData = dict()
    #!!! calculate frequency, median APM, prestige frequency, mastery frequency


def main():
    import pickle
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

    import json
    with open('ReplayData.json', 'w') as f:
        json.dump(ReplayData, f, indent=2)


    # 4352/5024 | 44.3s - base
    # 4352/5024 | 43.9 - no recovery
    # 4328/5024 | 42.1 - no lastest version
    # 4352/5024 | 44.7 - with MM excluded straight away    
    # 4328/5024 | 41.2 - no lastest
    # 4328/5024 | 4185 - with parsing events


    # # Get difficulty data
    # DifficultyData = calculate_difficulty_data(ReplayData)
    # print(f'{DifficultyData=}')

    # # Get map data
    # MapData = calculate_map_data(ReplayData)
    # print(f'{MapData=}')

    # # Get main commander data
    # CommanderData = calculate_commander_data(ReplayData, MainNames)
    # print(f'{CommanderData=}')

    # # Get ally commander frequencies
    # AllyCommanderData = calculate_ally_commander_data(ReplayData, MainNames)
    # print(f'{AllyCommanderData=}')









if __name__ == '__main__':
    main()
    # pass