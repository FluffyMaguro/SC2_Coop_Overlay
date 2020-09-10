"""
This module is used for generating overall stats from a list of replays (and player handles distinquishing between the main player and ally players)

"""
import os
import time
import pickle
import traceback
import statistics 

from SCOFunctions.MFilePath import truePath
from SCOFunctions.MLogging import logclass
from SCOFunctions.S2Parser import s2_parse_replay
from SCOFunctions.MainFunctions import find_names_and_handles, find_replays, names_fallback

logger = logclass('MASS','INFO')


def parse_replay(file):
    """ Parse replay with added exceptions and set key-arguments """
    try:
        return s2_parse_replay(file, try_lastest=False, parse_events=False, onlyBlizzard=True, withoutRecoverEnabled=True)
    except:
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
            MapData[r['map_name']] = {'Victory':0,'Defeat':0,'Fastest':{'length':3599},'average_victory_time':list()}

        MapData[r['map_name']][r['result']] += 1

        if r['result'] == 'Victory':
            MapData[r['map_name']]['average_victory_time'].append(r['accurate_length'])

        # Fastest clears
        if r['result'] == 'Victory' and r['accurate_length'] < MapData[r['map_name']]['Fastest']['length']:
            MapData[r['map_name']]['Fastest']['length'] = r['accurate_length']
            MapData[r['map_name']]['Fastest']['file'] = r['file']
            MapData[r['map_name']]['Fastest']['players'] = r['players'][1:3]
            MapData[r['map_name']]['Fastest']['enemy_race'] = r['enemy_race']
            MapData[r['map_name']]['Fastest']['date'] = r['date']
            MapData[r['map_name']]['Fastest']['difficulty'] = r['ext_difficulty']

    for m in MapData:
        if len(MapData[m]['average_victory_time']) > 0:
            MapData[m]['average_victory_time'] = statistics.mean(MapData[m]['average_victory_time'])
        else: 
            MapData[m]['average_victory_time'] = 3599

    return MapData


def get_masterises(replay,player):
    """ Return masteries. Contains fix for mastery switches (e.g. Zagara)"""
    masteries = replay['players'][player]['masteries']
    commander = replay['players'][player]['commander']

    # Zagara mastery fix (at least some)
    if commander == 'Zagara' and int(replay['date'].replace(':','')) < 20200825000000:
        masteries[2], masteries[5] = masteries[5], masteries[2]

    return masteries


def calculate_commander_data(ReplayData, main_handles):
    """ Calculates the number of wins and losses for each commander
    Returns separate objects for players with handles in MainHandles (capitalization not important) and those that are not"""
    CommanderData = dict()
    AllyCommanderData = dict()
    games = 0

    for r in ReplayData:
        for p in {1,2}:
            commander = r['players'][p]['commander']
            if r['players'][p]['handle'] in main_handles:
                if not commander in CommanderData:
                    CommanderData[commander] = {'Victory':0,'Defeat':0,'MedianAPM':list()}

                CommanderData[commander][r['result']] += 1
                CommanderData[commander]['MedianAPM'].append(r['players'][p]['apm'])
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
        CommanderData[commander]['MedianAPM'] = statistics.median(CommanderData[commander]['MedianAPM'])
        
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
            divisor = (mastery_summed_copy[(idx//2)*2] + mastery_summed_copy[(idx//2)*2+1])
            mastery_summed[idx] = 0 if divisor == 0 else mastery_summed[idx]/divisor

        AllyCommanderData[commander]['Mastery'] = mastery_summed

        # Prestige
        AllyCommanderData[commander]['Prestige'] = {i:AllyCommanderData[commander]['Prestige'].count(i)/len(AllyCommanderData[commander]['Prestige']) for i in {0,1,2,3}}

        # For ally correct frequency for the main player selecting certain commander (1/(1-f)) factor and rescale
        would_be_observed_games = (1/(1-CommanderData.get(commander,{'Frequency':0})['Frequency']))*(AllyCommanderData[commander]['Victory'] + AllyCommanderData[commander]['Defeat'])
        AllyCommanderData[commander]['Frequency'] = would_be_observed_games
        would_be_observed_games_total += would_be_observed_games

    for commander in AllyCommanderData:
        AllyCommanderData[commander]['Frequency'] = AllyCommanderData[commander]['Frequency']/would_be_observed_games_total

    return CommanderData, AllyCommanderData


class mass_replay_analysis:
    """ Class for mass replay analysis"""

    def __init__(self, ACCOUNTDIR):

        names, handles = find_names_and_handles(ACCOUNTDIR)

        self.main_names = names
        self.main_handles = handles
        self.replays = find_replays(ACCOUNTDIR)
        self.parsed_replays = set()
        self.ReplayData = list()
        self.cachefile = truePath('cache_overall_stats')


    def load_cache(self):
        """ Try to load previously parsed replays """
        try:
            if os.path.isfile(self.cachefile):
                with open(self.cachefile,'rb') as f:
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

        if len(self.main_names) == 0 and len(self.main_handles) > 0:
            self.main_names = names_fallback(self.main_handles, self.ReplayData)
            logger.info(f'No names from links. Falling back. New names:  {self.main_names}')


    def add_parsed_replay(self, parsed_data):
        """ Adds already parsed replay. Format has to be from my S2Parser"""
        if parsed_data != None and len(parsed_data) > 1 and not parsed_data['file'] in self.parsed_replays:
            self.ReplayData.append(parsed_data)
            self.parsed_replays.add(parsed_data['file'])


    def save_cache(self):
        """ Saves cache """
        with open(self.cachefile,'wb') as f:
            pickle.dump(self.ReplayData, f, protocol=pickle.HIGHEST_PROTOCOL)


    def update_accountdir(self, ACCOUNTDIR):
        """ Updates player handles and checks for new replays in the new accountdir.
        This doesn't remove replays that are no longer in the directory. """
        names, handles = find_names_and_handles(ACCOUNTDIR)
        replays = find_replays(ACCOUNTDIR)

        self.main_names = names
        self.main_handles = handles
        self.add_replays(replays)
        self.save_cache()


    def initialize(self):
        """ Executes full initialization """
        self.load_cache()
        self.add_replays(self.replays)
        self.save_cache()
        return True


    def get_last_replays(self, number):
        """ Returns an ordered list of last `number` replays from the newest to the oldest. """
        return sorted(self.ReplayData, key=lambda x: int(x['date'].replace(':','')), reverse=True)[:number]


    def main_player_is_sub_15(self, replay):
        """ Returns True if the main player is level 1-14"""
        for idx in {1,2}:
            if replay['players'][idx]['handle'] in self.main_handles and replay['players'][idx]['commander_level'] < 15:
                return True
        return False


    def both_main_players(self, replay):
        """ Checks if both players are the main players """
        if replay['players'][1]['handle'] in self.main_handles and replay['players'][2]['handle'] in self.main_handles:
            return True
        return False


    def analyse_replays(self, 
                        include_mutations=True, 
                        include_normal_games=True, 
                        mindate=None, maxdate=None, 
                        minlength=None, 
                        maxLength=None, 
                        difficulty_filter=None, 
                        region_filter=None, 
                        sub_15=True, 
                        over_15=True,
                        include_both_main=True,
                        ):
        """ Filters and analyses replays replay data
        `mindate` and `maxdate` has to be in a format of a long integer YYYYMMDDHHMMSS 
        `minLength` and `maxLength` in minutes 
        `difficulty_filter` is a list or set of difficulties to filter away: 'Casual', 'Normal', 'Hard', 'Brutal' or an integer (1-6) for Brutal+ games 
        `region_filter` is a list or set of regions to filter away: 'NA', 'EU', 'KR', 'CN', 'PTR' 
        `sub_15` = False if you want to filter out games where the main player was sub-15 commander level
        `over_15` = False if you want to exclude games where the main player is 15+
        `include_both_main` = False to exclude games where both players are main players
        """

        data = self.ReplayData

        if not include_mutations:
            data = [r for r in data if not r['extension']]

        if not include_normal_games:
            data = [r for r in data if r['extension']]

        if mindate != None:
            data = [r for r in data if int(r['date'].replace(':','')) > mindate]

        if maxdate != None:
            data = [r for r in data if int(r['date'].replace(':','')) < maxdate] 

        if minlength != None:
            data = [r for r in data if r['length'] >= minlength*60] 

        if maxLength != None:
            data = [r for r in data if r['length'] <= maxLength*60] 

        if difficulty_filter != None and len(difficulty_filter) > 0:
            logger.info(f'{difficulty_filter=}')
            for difficulty in difficulty_filter:
                if isinstance(difficulty, str):
                    data = [r for r in data if not difficulty in r['difficulty'] or r['brutal_plus'] > 0] # Don't filter out B+ if filtering out "Brutal"

                elif isinstance(difficulty, int):
                    data = [r for r in data if not difficulty == r['brutal_plus']]

        if region_filter != None and len(region_filter) > 0:
            logger.info(f'{region_filter=}')
            data = [r for r in data if not r['region'] in region_filter and r['region'] in {'NA','EU','KR','CN'}] 


        if not sub_15:
            data = [r for r in data if not self.main_player_is_sub_15(r)]

        if not over_15:
            data = [r for r in data if self.main_player_is_sub_15(r)]

        if not include_both_main:
            data = [r for r in data if not self.both_main_players(r)]


        logger.info(f'Filtering {len(self.ReplayData)} → {len(data)}')

        # Analyse
        DifficultyData = calculate_difficulty_data(data)
        MapData = calculate_map_data(data)
        CommanderData, AllyCommanderData = calculate_commander_data(data, self.main_handles)

        return {'DifficultyData':DifficultyData,'MapData':MapData,'CommanderData':CommanderData,'AllyCommanderData':AllyCommanderData, 'games': len(data)}


def mass_replay_analysis_thread(ACCOUNTDIR):
    """ Main thread for mass replay analysis. Handles all initialization. """

    CAnalysis = mass_replay_analysis(ACCOUNTDIR)
    CAnalysis.initialize()
    return CAnalysis