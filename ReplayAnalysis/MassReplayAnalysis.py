"""
This module is used for generating overall stats from a list of replays (and main names distinquishing between the main player and ally players)

"""

import os
import time
import pickle
import traceback
import statistics 

from ReplayAnalysis.MLogging import logclass
from ReplayAnalysis.S2Parser import s2_parse_replay

logger = logclass('MREP','INFO')



def parse_replay(file):
    """ Parse replay with added exceptions and set key-arguments """
    try:
        return s2_parse_replay(file, try_lastest=False, parse_events=False, onlyBlizzard=True, withoutRecoverEnabled=True)
    except:
        logger.error(file,traceback.format_exc())
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

    for diff in DifficultyData:
        DifficultyData[diff]['Winrate'] = DifficultyData[diff]['Victory']/(DifficultyData[diff]['Victory'] + DifficultyData[diff]['Defeat'])

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


def get_masterises(replay,player):
    """ Return masteries. Contains fix for mastery switches (e.g. Zagara)"""
    masteries = replay['players'][player]['masteries']
    commander = replay['players'][player]['commander']

    # Zagara mastery fix (at least some)
    if commander == 'Zagara' and int(replay['date'].replace(':','')) < 20200825000000:
        masteries[2], masteries[5] = masteries[5], masteries[2]

    return masteries


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
                masteries = get_masterises(r,p)
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
            mastery_summed[idx] = mastery_summed[idx]/(mastery_summed_copy[(idx//2)*2] + mastery_summed_copy[(idx//2)*2+1])

        AllyCommanderData[commander]['Mastery'] = mastery_summed

        # Prestige
        AllyCommanderData[commander]['Prestige'] = {i:AllyCommanderData[commander]['Prestige'].count(i)/len(AllyCommanderData[commander]['Prestige']) for i in {0,1,2,3}}

        # For ally correct frequency for the main player selecting certain commander (1/(1-f)) factor and rescale
        would_be_observed_games = (1/(1-CommanderData[commander]['Frequency']))*(AllyCommanderData[commander]['Victory'] + AllyCommanderData[commander]['Defeat'])
        AllyCommanderData[commander]['Frequency'] = would_be_observed_games
        would_be_observed_games_total += would_be_observed_games

    for commander in AllyCommanderData:
        AllyCommanderData[commander]['Frequency'] = AllyCommanderData[commander]['Frequency']/would_be_observed_games_total

    return CommanderData, AllyCommanderData


class mass_replay_analysis:
    """ Class for mass replay analysis"""

    def __init__(self, main_names):
        self.main_names = main_names
        self.parsed_replays = set()
        self.ReplayData = list()


    def load_cache(self):
        """ Try to load previously parsed replays """
        try:
            if os.path.isfile('cache_overallstats'):
                with open('cache_overallstats','rb') as f:
                    self.ReplayData = pickle.load(f)

                self.parsed_replays = {r['file'] for r in self.ReplayData}
        except:
            logger.error(traceback.format_exc())


    def add_replays(self,replays):
        """ Parses and adds new replays. Doesn't parse already parsed replays. """
        replays_to_parse = {r for r in replays if not r in self.parsed_replays}
        ts = time.time()
        self.ReplayData = self.ReplayData + list(map(parse_replay, replays_to_parse))
        self.ReplayData = [r for r in self.ReplayData if r != None]
        self.parsed_replays = self.parsed_replays.union(replays_to_parse)
        logger.info(f'Parsing {len(replays_to_parse)} replays in {time.time()-ts:.1f} seconds leaving us with {len(self.ReplayData)} games')


    def save_cache(self):
        """ Saves cache """
        with open('cache_overallstats','wb') as f:
            pickle.dump(self.ReplayData, f, protocol=pickle.HIGHEST_PROTOCOL)


    def initialize(self, replays):
        """ Executes full initialization """
        self.load_cache()
        self.add_replays(replays)
        self.save_cache()


    def analyse_replays(self, include_mutations=True, include_normal_games=True, mindate=None, maxdate=None):
        """ Filters and analyses replays replay data
        `mindate` and `maxdate` has to be in a format of a long integer YYYYMMDDHHMMSS """
        data = self.ReplayData

        if not include_mutations:
            data = [r for r in data if not r['extension'] and not r['brutal_plus'] > 0]

        if not include_normal_games:
            data = [r for r in data if r['extension'] or r['brutal_plus'] > 0]

        if mindate != None:
            data = [r for r in data if int(r['date'].replace(':','')) > mindate]

        if maxdate != None:
            data = [r for r in data if int(r['date'].replace(':','')) < maxdate]    

        logger.info(f'Filtering {len(self.ReplayData)} → {len(data)}')

        # Analyse
        DifficultyData = calculate_difficulty_data(data)
        MapData = calculate_map_data(data)
        CommanderData, AllyCommanderData = calculate_commander_data(data, self.main_names)

        return {'DifficultyData':DifficultyData,'MapData':MapData,'CommanderData':CommanderData,'AllyCommanderData':AllyCommanderData}

