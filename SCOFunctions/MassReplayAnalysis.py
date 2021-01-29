"""
This module is used for generating overall stats from a list of replays (and player handles distinquishing between the main player and ally players)

"""
import os
import time
import json
import pickle
import hashlib
import traceback
import statistics
import s2protocol
import threading

from SCOFunctions.MFilePath import truePath
from SCOFunctions.MLogging import logclass
from SCOFunctions.S2Parser import s2_parse_replay
from SCOFunctions.ReplayAnalysis import analyse_replay
from SCOFunctions.MainFunctions import find_names_and_handles, find_replays, names_fallback
from SCOFunctions.SC2Dictionaries import bonus_objectives, mc_units

logger = logclass('MASS', 'INFO')
lock = threading.Lock()


def parse_replay(file):
    """ Parse replay with added exceptions and set key-arguments """
    try:
        return s2_parse_replay(file, try_lastest=True, parse_events=False, onlyBlizzard=True, withoutRecoverEnabled=True)
    except s2protocol.decoders.TruncatedError:
        return None
    except:
        logger.error(traceback.format_exc())
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
            DifficultyData[diff] = {'Victory': 0, 'Defeat': 0}

        DifficultyData[diff][r['result']] += 1

    for diff in DifficultyData:
        DifficultyData[diff]['Winrate'] = DifficultyData[diff]['Victory'] / (DifficultyData[diff]['Victory'] + DifficultyData[diff]['Defeat'])

    return DifficultyData


def calculate_map_data(ReplayData):
    """ Calculates the number of wins and losses for each map """
    MapData = dict()

    for r in ReplayData:
        if not r['map_name'] in MapData:
            MapData[r['map_name']] = {'Victory': 0, 'Defeat': 0, 'Fastest': {'length': 999999}, 'average_victory_time': list(), 'bonus': list()}

        MapData[r['map_name']][r['result']] += 1

        if r['result'] == 'Victory':
            MapData[r['map_name']]['average_victory_time'].append(r['accurate_length'])

            # Append a fraction of bonus completed
            if 'bonus' in r:
                MapData[r['map_name']]['bonus'].append(len(r['bonus']) / bonus_objectives[r['map_name']])

        # Fastest clears
        if r['result'] == 'Victory' and r['accurate_length'] < MapData[r['map_name']]['Fastest']['length']:
            MapData[r['map_name']]['Fastest']['length'] = r['accurate_length']
            MapData[r['map_name']]['Fastest']['file'] = r['file']
            MapData[r['map_name']]['Fastest']['players'] = r['players'][1:3]
            MapData[r['map_name']]['Fastest']['enemy_race'] = r['enemy_race']
            MapData[r['map_name']]['Fastest']['date'] = r['date']
            MapData[r['map_name']]['Fastest']['difficulty'] = r['ext_difficulty']

    for m in MapData:
        MapData[m]['frequency'] = (MapData[m]['Victory'] + MapData[m]['Defeat']) / len(ReplayData)
        MapData[m]['winrate'] = MapData[m]['Victory'] / (MapData[m]['Victory'] + MapData[m]['Defeat'])
        if len(MapData[m]['average_victory_time']) > 0:
            MapData[m]['average_victory_time'] = statistics.mean(MapData[m]['average_victory_time'])
        else:
            MapData[m]['average_victory_time'] = 999999

        if len(MapData[m]['bonus']) > 0:
            MapData[m]['bonus'] = sum(MapData[m]['bonus']) / len(MapData[m]['bonus'])
        else:
            MapData[m]['bonus'] = 0

    return MapData


def get_masterises(replay, player):
    """ Return masteries. Contains fix for mastery switches (e.g. Zagara)"""
    masteries = replay['players'][player]['masteries'].copy()
    commander = replay['players'][player]['commander']

    # Zagara mastery fix (at least some)
    if commander == 'Zagara' and int(replay['date'].replace(':', '')) < 20200825000000:
        masteries[2], masteries[5] = masteries[5], masteries[2]

    return masteries


def calculate_commander_data(ReplayData, main_handles):
    """ Calculates the number of wins and losses for each commander
    Returns separate objects for players with handles in MainHandles (capitalization not important) and those that are not"""
    CommanderData = dict()
    AllyCommanderData = dict()
    games = 0
    CommanderData['any'] = {'Victory': 0, 'Defeat': 0, 'MedianAPM': list(), 'KillFraction': list()}
    AllyCommanderData['any'] = {'Victory': 0, 'Defeat': 0, 'MedianAPM': list(), 'KillFraction': list()}

    for r in ReplayData:
        total_kills = r['players'][1].get('kills', 0) + r['players'][2].get('kills', 0)
        for p in (1, 2):
            commander = r['players'][p]['commander']
            if r['players'][p]['handle'] in main_handles:
                if not commander in CommanderData:
                    CommanderData[commander] = {
                        'Victory': 0,
                        'Defeat': 0,
                        'MedianAPM': list(),
                        'Prestige': list(),
                        'Mastery': list(),
                        'KillFraction': list()
                    }

                CommanderData[commander][r['result']] += 1
                CommanderData[commander]['MedianAPM'].append(r['players'][p]['apm'])
                CommanderData['any'][r['result']] += 1
                CommanderData['any']['MedianAPM'].append(r['players'][p]['apm'])

                if total_kills > 0:
                    CommanderData[commander]['KillFraction'].append(r['players'][p]['kills'] / total_kills)
                    CommanderData['any']['KillFraction'].append(r['players'][p]['kills'] / total_kills)

                games += 1

                # Count prestige only after they were released
                if int(r['date'].replace(':', '')) > 20200726000000:
                    CommanderData[commander]['Prestige'].append(r['players'][p]['prestige'])

                # Add masteries, use relative values to properly reflect player preferences
                masteries = get_masterises(r, p)
                mastery_sum = sum(masteries) / 3
                masteries = [m / mastery_sum for m in masteries] if mastery_sum != 0 else masteries
                CommanderData[commander]['Mastery'].append(masteries)

            else:
                if not commander in AllyCommanderData:
                    AllyCommanderData[commander] = {
                        'Victory': 0,
                        'Defeat': 0,
                        'MedianAPM': list(),
                        'Prestige': list(),
                        'Mastery': list(),
                        'KillFraction': list()
                    }

                AllyCommanderData[commander][r['result']] += 1
                AllyCommanderData[commander]['MedianAPM'].append(r['players'][p]['apm'])
                if total_kills > 0:
                    AllyCommanderData[commander]['KillFraction'].append(r['players'][p]['kills'] / total_kills)
                    AllyCommanderData['any']['KillFraction'].append(r['players'][p]['kills'] / total_kills)

                # Count prestige only after they were released
                if int(r['date'].replace(':', '')) > 20200726000000:
                    AllyCommanderData[commander]['Prestige'].append(r['players'][p]['prestige'])

                AllyCommanderData['any'][r['result']] += 1
                AllyCommanderData['any']['MedianAPM'].append(r['players'][p]['apm'])

                # Add masteries, use relative values to properly reflect player preferences
                masteries = get_masterises(r, p)
                mastery_sum = sum(masteries) / 3
                masteries = [m / mastery_sum for m in masteries] if mastery_sum != 0 else masteries
                AllyCommanderData[commander]['Mastery'].append(masteries)

    # Main player
    for commander in CommanderData:
        com_games = len(CommanderData[commander]['MedianAPM'])
        CommanderData[commander]['Frequency'] = 0 if games == 0 else com_games / games
        CommanderData[commander]['Winrate'] = 0 if com_games == 0 else CommanderData[commander]['Victory'] / len(
            CommanderData[commander]['MedianAPM'])
        CommanderData[commander]['MedianAPM'] = 0 if com_games == 0 else statistics.median(CommanderData[commander]['MedianAPM'])

        # Fraction kills
        if len(CommanderData[commander]['KillFraction']) > 0:
            CommanderData[commander]['KillFraction'] = statistics.median(CommanderData[commander]['KillFraction'])
        else:
            CommanderData[commander]['KillFraction'] = 0

        if commander != 'any':
            # Mastery (sum list of lists, normalize)
            mastery_summed = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for i in CommanderData[commander]['Mastery']:
                for idx, m in enumerate(i):
                    mastery_summed[idx] += m

            # Normalize mastery choices
            mastery_summed_copy = mastery_summed.copy()
            for idx, m in enumerate(mastery_summed):
                divisor = (mastery_summed_copy[(idx // 2) * 2] + mastery_summed_copy[(idx // 2) * 2 + 1])
                mastery_summed[idx] = 0 if divisor == 0 else mastery_summed[idx] / divisor

            CommanderData[commander]['Mastery'] = mastery_summed

            # Prestige
            if len(CommanderData[commander]['Prestige']) > 0:
                CommanderData[commander]['Prestige'] = {
                    i: CommanderData[commander]['Prestige'].count(i) / len(CommanderData[commander]['Prestige'])
                    for i in (0, 1, 2, 3)
                }
            else:
                CommanderData[commander]['Prestige'] = {0: 0, 1: 0, 2: 0, 3: 0}

    # Ally
    would_be_observed_games_total = 0
    for commander in AllyCommanderData:
        com_games = len(AllyCommanderData[commander]['MedianAPM'])

        # Fraction kills
        if len(AllyCommanderData[commander]['KillFraction']) > 0:
            AllyCommanderData[commander]['KillFraction'] = statistics.median(AllyCommanderData[commander]['KillFraction'])
        else:
            AllyCommanderData[commander]['KillFraction'] = 0

        # Winrate
        AllyCommanderData[commander]['Winrate'] = 0 if com_games == 0 else AllyCommanderData[commander]['Victory'] / com_games

        # APM
        AllyCommanderData[commander]['MedianAPM'] = 0 if com_games == 0 else statistics.median(AllyCommanderData[commander]['MedianAPM'])

        if commander != 'any':
            # Mastery (sum list of lists, normalize)
            mastery_summed = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for i in AllyCommanderData[commander]['Mastery']:
                for idx, m in enumerate(i):
                    mastery_summed[idx] += m

            # Normalize mastery choices
            mastery_summed_copy = mastery_summed.copy()
            for idx, m in enumerate(mastery_summed):
                divisor = (mastery_summed_copy[(idx // 2) * 2] + mastery_summed_copy[(idx // 2) * 2 + 1])
                mastery_summed[idx] = 0 if divisor == 0 else mastery_summed[idx] / divisor

            AllyCommanderData[commander]['Mastery'] = mastery_summed

            # Prestige
            if len(AllyCommanderData[commander]['Prestige']) > 0:
                AllyCommanderData[commander]['Prestige'] = {
                    i: AllyCommanderData[commander]['Prestige'].count(i) / len(AllyCommanderData[commander]['Prestige'])
                    for i in (0, 1, 2, 3)
                }
            else:
                AllyCommanderData[commander]['Prestige'] = {0: 0, 1: 0, 2: 0, 3: 0}

            # For ally correct frequency for the main player selecting certain commander (1/(1-f)) factor and rescale
            would_be_observed_games = (1 / (1 - CommanderData.get(commander, {'Frequency': 0})['Frequency'])) * com_games
            AllyCommanderData[commander]['Frequency'] = would_be_observed_games
            would_be_observed_games_total += would_be_observed_games

    AllyCommanderData['any']['Frequency'] = would_be_observed_games_total
    for commander in AllyCommanderData:
        AllyCommanderData[commander][
            'Frequency'] = 0 if would_be_observed_games_total == 0 else AllyCommanderData[commander]['Frequency'] / would_be_observed_games_total

    return CommanderData, AllyCommanderData


def calculate_region_data(ReplayData, main_handles):
    """ Calculates region data - frequency, wins, losses, winrate, max ascension level, leveled commanders """
    dRegion = dict()
    for r in ReplayData:
        if not r['region'] in dRegion:
            dRegion[r['region']] = {'Victory': 0, 'Defeat': 0, 'max_asc': 0, 'max_com': set(), 'prestiges': dict()}

        dRegion[r['region']][r['result']] += 1

        for p in (1, 2):
            if r['players'][p]['handle'] in main_handles:
                # Add leveled commanders:
                if r['players'][p]['commander_level'] == 15:
                    dRegion[r['region']]['max_com'].add(r['players'][p]['commander'])
                # Track max ascension
                if r['players'][p]['commander_mastery_level'] > dRegion[r['region']]['max_asc']:
                    dRegion[r['region']]['max_asc'] = r['players'][p]['commander_mastery_level']

                if r['players'][p]['prestige'] > 0:
                    if not r['players'][p]['commander'] in dRegion[r['region']]['prestiges']:
                        dRegion[r['region']]['prestiges'][r['players'][p]['commander']] = set()

                    dRegion[r['region']]['prestiges'][r['players'][p]['commander']].add(r['players'][p]['prestige'])

    for region in dRegion:
        dRegion[region]['winrate'] = dRegion[region]['Victory'] / (dRegion[region]['Victory'] + dRegion[region]['Defeat'])
        dRegion[region]['frequency'] = (dRegion[region]['Victory'] + dRegion[region]['Defeat']) / len(ReplayData)

    return dRegion


def _add_units(unit_data: dict, r: dict, p: int):
    """ Add units to the dictionary"""

    if not 'units' in r['players'][p]:
        return

    commander = r['players'][p]['commander']
    if not commander in unit_data:
        unit_data[commander] = dict()
        unit_data[commander]['count'] = 0

    unit_data[commander]['count'] += 1

    # Count kills done by mind-controlled units
    mc_unit_bonus_kills = 0
    if commander in mc_units and mc_units[commander] in r['players'][p]['units']:
        for unit in r['players'][p]['units']:
            # If unit wasn't created, but still got kills
            if r['players'][p]['units'][unit][0] == 0 or (commander == 'Karax' and unit == 'Disruptor') or (commander != 'Tychus'
                                                                                                            and unit == 'Auto-Turret'):
                mc_unit_bonus_kills += r['players'][p]['units'][unit][2]

    # Go over units
    for unit in r['players'][p]['units']:
        # Don't count units without kills
        if r['players'][p]['units'][unit][2] <= 0:
            continue

        if not unit in unit_data[commander]:
            unit_data[commander][unit] = {'created': 0, 'lost': 0, 'kills': 0, 'kill_percentage': list()}

        # Add unit [created, lost, kills]
        names = {0: 'created', 1: 'lost', 2: 'kills'}
        for i, s in names.items():
            if not isinstance(r['players'][p]['units'][unit][i], str) and not isinstance(unit_data[commander][unit][s], str):
                unit_data[commander][unit][s] += r['players'][p]['units'][unit][i]
            else:
                unit_data[commander][unit][s] = r['players'][p]['units'][unit][i]

        # Add bonus kills to mind-controlling unit
        if mc_unit_bonus_kills > 0 and unit == mc_units[commander]:
            unit_data[commander][unit]['kills'] += mc_unit_bonus_kills
            kills_ingame = r['players'][p]['units'][unit][2] + mc_unit_bonus_kills
            unit_data[commander][unit]['kill_percentage'].append(kills_ingame / r['players'][p]['kills'])
            mc_unit_bonus_kills = 0

        # Calculate kill fraction for the rest
        elif r['players'][p]['kills'] > 0:
            unit_data[commander][unit]['kill_percentage'].append(r['players'][p]['units'][unit][2] / r['players'][p]['kills'])


def _add_units_amon(unit_data: dict, r: dict):
    """ Add units from the replay into amon's dictionary"""
    if not 'amon_units' in r:
        return
    for unit in r['amon_units']:
        if not unit in unit_data:
            unit_data[unit] = {'created': 0, 'lost': 0, 'kills': 0}

        names = {0: 'created', 1: 'lost', 2: 'kills'}
        for i in range(3):
            if isinstance(r['amon_units'][unit][i], int) or isinstance(r['amon_units'][unit][i], float):
                unit_data[unit][names[i]] += r['amon_units'][unit][i]


def _process_dict_amon(unit_data: dict):
    """ Sorts and calculates KD for Amon's dictionary"""
    # Calculate K/D
    total = {'created': 0, 'lost': 0, 'kills': 0}

    for unit in unit_data:
        # These mutator units shouldn't have any losses
        if unit in ('Twister', 'Purifier Beam', 'Moebius Corps Laser Drill', 'Blizzard'):
            unit_data[unit]['lost'] = 0
            unit_data[unit]['KD'] = '-'
        elif unit_data[unit]['lost'] > 0:
            unit_data[unit]['KD'] = unit_data[unit]['kills'] / unit_data[unit]['lost']
        else:
            unit_data[unit]['KD'] = 0

        # Add total
        total['created'] += unit_data[unit]['created']
        total['lost'] += unit_data[unit]['lost']
        total['kills'] += unit_data[unit]['kills']

    total['KD'] = 0
    if total['lost'] > 0:
        total['KD'] = total['kills'] / total['lost']
    """
     Remove these units. 
     Drakken Pulse Cannon is the nuke effect on Cradle of Death. 
     Sirius Sykes' kills is his autoturrets being captured by Eminent Domain and kills added to him.
     AdeptPhaseShift is probably from Eminent Domain as well.

     """
    for unit in ('AdeptPhaseShift', 'Drakken Pulse Cannon', "James 'Sirius' Sykes"):
        if unit in unit_data:
            del unit_data[unit]

    # Sort
    unit_data['sum'] = total
    unit_data = {k: v for k, v in sorted(unit_data.items(), key=lambda x: x[1]['created'], reverse=True)}

    # I need to return here because it's sorted. In case of commander dicts, the sorting is in inner dictionaries and is passed
    return unit_data


def _process_dict(unit_data: dict):
    """ Calculates median kill percentages, K/D, lost_percent"""
    for commander in unit_data:
        total = {'created': 0, 'lost': 0, 'kills': 0, 'kill_percentage': 1}

        for unit in unit_data[commander]:
            if unit in ('sum', 'count'):
                continue

            # Calculate median of kills
            if len(unit_data[commander][unit]['kill_percentage']) > 0:
                unit_data[commander][unit]['kill_percentage'] = statistics.median(unit_data[commander][unit]['kill_percentage'])
            else:
                unit_data[commander][unit]['kill_percentage'] = 0

            # Calculate K/D
            if not isinstance(unit_data[commander][unit]['lost'], str) and unit_data[commander][unit]['lost'] > 0:
                unit_data[commander][unit]['KD'] = unit_data[commander][unit]['kills'] / unit_data[commander][unit]['lost']
            else:
                unit_data[commander][unit]['KD'] = None

            # Calculate lost percent
            if not isinstance(unit_data[commander][unit]['created'], str) and not isinstance(unit_data[commander][unit]['lost'],
                                                                                             str) and unit_data[commander][unit]['created'] > 0:
                unit_data[commander][unit]['lost_percent'] = unit_data[commander][unit]['lost'] / unit_data[commander][unit]['created']
            else:
                unit_data[commander][unit]['lost_percent'] = None

            # Sum
            if unit in ('Mecha Infestor', 'Havoc', 'SCV', 'Probe', 'Drone', 'Mecha Drone', 'Primal Drone', 'Infested SCV', 'Probius',
                        'Dominion Laborer', 'Primal Hive', 'Primal Warden', 'Imperial Intercessor', 'Archangel'):
                continue
            if commander != 'Tychus' and unit == 'Auto-Turret':
                continue
            for item in ('created', 'lost', 'kills'):
                if not isinstance(unit_data[commander][unit][item], str):
                    total[item] += unit_data[commander][unit][item]

        # Sum K/D
        if total['lost'] > 0:
            total['KD'] = total['kills'] / total['lost']
        else:
            total['KD'] = 0

        # Sum lost percent
        if total['created'] > 0:
            total['lost_percent'] = total['lost'] / total['created']
        else:
            total['lost_percent'] = 0

        unit_data[commander]['sum'] = total


def calculate_unit_stats(ReplayData, main_handles):
    """ Calculates stats for each unit type for player, allies and Amon.
    This includes number of kills, created and lost for all unit types and sum"""

    main_unit_data = dict()
    ally_unit_data = dict()
    amon_unit_data = dict()

    for r in ReplayData:
        _add_units_amon(amon_unit_data, r)
        for p in (1, 2):
            if r['players'][p]['handle'] in main_handles:
                _add_units(main_unit_data, r, p)
            else:
                _add_units(ally_unit_data, r, p)

    _process_dict(main_unit_data)
    _process_dict(ally_unit_data)
    amon_unit_data = _process_dict_amon(amon_unit_data)

    return {'main': main_unit_data, 'ally': ally_unit_data, 'amon': amon_unit_data}


def calculate_words(ReplayData):
    """ Caulculates which words were used and how many times"""

    words = dict()
    for r in ReplayData:
        for m in r['messages']:
            message = m['text'].split(' ')
            for word in message:
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1

    return {k: v for k, v in sorted(words.items(), key=lambda x: x[1], reverse=True)}


class mass_replay_analysis:
    """ Class for mass replay analysis"""
    def __init__(self, ACCOUNTDIR):

        names, handles = find_names_and_handles(ACCOUNTDIR)

        self.main_names = names
        self.main_handles = handles
        self.parsed_replays = set()
        self.ReplayData = list()
        self.ReplayDataAll = list()
        self.cachefile = truePath('cache_overall_stats')
        self.winrate_data = dict()
        self.current_replays = find_replays(ACCOUNTDIR)
        self.closing = False
        self.full_analysis_label = None
        self.full_analysis_finished = False
        self.name_handle_dict = dict()

    def search(self, *args):
        """ Returns a sorted list of replays containining given arguments in their data structure"""
        replays = list()
        args = tuple(str(a).lower() for a in args)
        races = ('terran', 'protoss', 'zerg')

        for r in self.ReplayData:
            struct = str(r).lower()
            args_found = 0
            for arg in args:
                # Special filter for races. Check enemy race directly.
                if arg in races:
                    if arg == r['enemy_race'].lower():
                        args_found += 1

                elif arg in struct:
                    args_found += 1

            if args_found == len(args):
                replays.append(r)

        return sorted(replays, key=lambda x: int(x['date'].replace(':', '')), reverse=True)

    def load_cache(self):
        """ Try to load previously parsed replays """
        try:
            if os.path.isfile(self.cachefile):
                with open(self.cachefile, 'rb') as f:
                    self.ReplayDataAll = pickle.load(f)

                self.parsed_replays = {r.get('hash', self.get_hash(r['file'])) for r in self.ReplayDataAll}
        except:
            logger.error(traceback.format_exc())

    def add_replays(self, replays):
        """ Parses and adds new replays. Doesn't parse already parsed replays. """

        ts = time.time()
        out = list()
        new_hashes = set()
        new_files = set()

        for r in replays:
            rhash = self.get_hash(r)
            if not rhash in self.parsed_replays:
                out.append(parse_replay(r))
                new_hashes.add(rhash)
                new_files.add(r)
                if self.closing:
                    break

        out += self.ReplayDataAll
        out = [r for r in out if r != None]

        with lock:
            self.ReplayDataAll = out
            self.parsed_replays = self.parsed_replays.union(new_hashes)
            self.current_replays = self.current_replays.union(new_files)
            self.update_data()

        logger.info(f'Parsing {len(new_hashes)} replays in {time.time()-ts:.1f} seconds leaving us with {len(self.ReplayData)} games')

        if len(self.main_names) == 0 and len(self.main_handles) > 0:
            self.main_names = names_fallback(self.main_handles, self.ReplayDataAll)
            logger.info(f'No names from links. Falling back. New names:  {self.main_names}')

    def add_parsed_replay(self, full_data):
        """ Adds already parsed replay. Format has to be from my S2Parser"""
        parsed_data = full_data.get('parser')

        if parsed_data != None and \
            len(parsed_data) > 1 and \
            not '[MM]' in parsed_data['file'] and \
            parsed_data['isBlizzard'] and \
            len(parsed_data['players']) > 2 and \
            parsed_data['players'][1].get('commander') != None:

            parsed_data = self.format_data(full_data)

            with lock:
                self.ReplayDataAll.append(parsed_data)
                self.parsed_replays.add(parsed_data['hash'])
                self.current_replays.add(parsed_data['file'])
                self.update_data()

    def format_data(self, full_data):
        """ Formats data returned by replay analysis into a single datastructure used here"""
        parsed_data = full_data['parser']
        parsed_data['accurate_length'] = full_data['length'] * 1.4
        parsed_data['bonus'] = full_data['bonus']
        parsed_data['comp'] = full_data['comp']
        parsed_data['amon_units'] = full_data['amonUnits']
        parsed_data['full_analysis'] = True
        parsed_data['hash'] = parsed_data.get('hash', self.get_hash(full_data['filepath']))

        main = full_data['positions']['main']
        for p in (1, 2):
            parsed_data['players'][p]['kills'] = full_data['mainkills'] if p == main else full_data['allykills']
            parsed_data['players'][p]['icons'] = full_data['mainIcons'] if p == main else full_data['allyIcons']
            parsed_data['players'][p]['units'] = full_data['mainUnits'] if p == main else full_data['allyUnits']
        return parsed_data

    def save_cache(self):
        """ Saves cache """
        with lock:
            with open(self.cachefile, 'wb') as f:
                pickle.dump(self.ReplayDataAll, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def get_hash(file):
        """ Returns MD5 file hash for a file """
        try:
            with open(file, "rb") as f:
                bytesread = f.read()
                readable_hash = hashlib.md5(bytesread).hexdigest()
            return readable_hash
        except:
            logger.error(traceback.format_exc())
            return None

    def dump_all(self):
        """ Dumps all data to a json file """
        file_name = 'replay_data_dump.json'
        data = dict()
        # Load previous file if there is one
        if os.path.isfile(file_name):
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
            except:
                logger.error(traceback.format_exc())

        # Go through current replays, get file hashes, see if they are added
        for r in self.ReplayDataAll:
            if not 'hash' in r:
                r['hash'] = self.get_hash(r['file'])

            data[r['hash']] = r

        # Save file again
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)

    def update_accountdir(self, ACCOUNTDIR):
        """ Updates player handles and checks for new replays in the new accountdir.
        This doesn't remove replays that are no longer in the directory. """
        names, handles = find_names_and_handles(ACCOUNTDIR)
        replays = find_replays(ACCOUNTDIR)

        self.main_names = names
        self.main_handles = handles
        self.add_replays(replays)
        self.current_replays = replays
        self.update_data()
        self.save_cache()
        self.update_name_handle_dict()

    def update_data(self, showAll=False):
        """ Updates current data """
        if showAll:
            self.ReplayData = self.ReplayDataAll
        else:
            self.ReplayData = [r for r in self.ReplayDataAll if r['file'] in self.current_replays]

    def initialize(self):
        """ Executes full initialization """
        self.load_cache()
        self.add_replays(self.current_replays)
        self.save_cache()
        self.update_name_handle_dict()
        return True

    def update_name_handle_dict(self):
        """ Udpates disctionary of names and handles 
        Lists corresponding player names to handles"""
        for i in range(len(self.ReplayDataAll) - 1, -1, -1):  #Iterate in reverse order
            if len(self.name_handle_dict) == len(self.main_handles):
                break

            for p in (1, 2):
                handle = self.ReplayDataAll[i]['players'][p]['handle']
                if handle in self.main_handles and not handle in self.name_handle_dict:
                    self.name_handle_dict[handle] = self.ReplayDataAll[i]['players'][p]['name']

    def get_last_replays(self, number):
        """ Returns an ordered list of last `number` replays from the newest to the oldest. """
        return sorted(self.ReplayData, key=lambda x: int(x['date'].replace(':', '')), reverse=True)[:number]

    def run_full_analysis(self):
        """ Run full analysis on all replays """
        self.closing = False

        # Get current status & updated
        fully_parsed = 0
        for r in self.ReplayDataAll:
            if 'full_analysis' in r or 'comp' in r:
                fully_parsed += 1
        self.full_analysis_label.setText(f'Running... {fully_parsed}/{len(self.ReplayDataAll)} ({100*fully_parsed/len(self.ReplayDataAll):.0f}%)')
        fully_parsed_at_start = fully_parsed

        # Start
        logger.info('Starting full analysis!')
        start = time.time()
        idx = 0
        eta = '?'
        for r in self.ReplayDataAll:
            # Save cache every now and then
            if idx >= 20:
                idx = 0
                self.save_cache()

            # Interrupt the analysis if the app is closing
            if self.closing:
                self.save_cache()
                return False

            # Analyze those that are not fully parsed yet
            if not 'full_analysis' in r and not 'comp' in r:
                if not os.path.isfile(r['file']):
                    continue

                full_data = analyse_replay(r['file'])

                full_data['full_analysis'] = True
                if len(full_data) < 2:
                    with lock:
                        r['full_analysis'] = False
                    continue

                # Update data
                idx += 1
                fully_parsed += 1

                # Calculate eta
                if (fully_parsed - fully_parsed_at_start) > 15 and (fully_parsed - fully_parsed_at_start) % 3 == 0:
                    eta = (len(self.ReplayDataAll) - fully_parsed) / ((fully_parsed - fully_parsed_at_start) / (time.time() - start))
                    eta = time.strftime("%H:%M:%S", time.gmtime(eta))

                # Update widget
                with lock:
                    try:
                        formated = self.format_data(full_data)
                        r.update(formated)
                    except:
                        logger.error(traceback.format_exc())
                    self.full_analysis_label.setText(
                        f'Estimated remaining time: {eta}\nRunning... {fully_parsed}/{len(self.ReplayDataAll)} ({100*fully_parsed/len(self.ReplayDataAll):.0f}%)'
                    )

        if idx > 0:
            self.save_cache()
        self.full_analysis_label.setText(
            f'Full analysis completed! {fully_parsed}/{len(self.ReplayDataAll)} | {100*fully_parsed/len(self.ReplayDataAll):.0f}%')
        logger.info(f'Full analysis completed in {time.time()-start:.0f} seconds!')
        self.full_analysis_finished = True
        return True

    def main_player_is_sub_15(self, replay):
        """ Returns True if the main player is level 1-14"""
        for idx in (1, 2):
            if replay['players'][idx]['handle'] in self.main_handles and replay['players'][idx]['commander_level'] < 15:
                return True
        return False

    def both_main_players(self, replay):
        """ Checks if both players are the main players """
        try:
            if replay['players'][1]['handle'] in self.main_handles and replay['players'][2]['handle'] in self.main_handles:
                return True
            return False
        except:
            logger.error(f"{replay}\n{traceback.format_exc()}")

    def calculate_player_winrate_data(self):
        """ Calculates player winrate data """
        winrate_data = dict()
        for replay in self.ReplayData:
            for p in (1, 2):
                player = replay['players'][p]['name']
                if not player in winrate_data:
                    winrate_data[player] = [0, 0, list(), list(), 0]  # Wins, losses, apm, commander, commander frequency

                if replay['result'] == 'Victory':
                    winrate_data[player][0] += 1
                else:
                    winrate_data[player][1] += 1

                winrate_data[player][2].append(replay['players'][p]['apm'])
                winrate_data[player][3].append(replay['players'][p]['commander'])

        for player in winrate_data:
            # Median APM
            if len(winrate_data[player][2]) > 0:
                winrate_data[player][2] = statistics.median(winrate_data[player][2])
            else:
                winrate_data[player][2] = 0

            # Commander mode and frequency
            if len(winrate_data[player][3]) > 0:
                mode = statistics.mode(winrate_data[player][3])
                winrate_data[player][4] = winrate_data[player][3].count(mode) / len(winrate_data[player][3])
                winrate_data[player][3] = mode
            else:
                winrate_data[player][3] = ''

        # Sort by wins
        winrate_data = {k: v for k, v in sorted(winrate_data.items(), key=lambda x: x[1][0], reverse=True)}
        self.winrate_data = winrate_data
        return winrate_data

    def find_banks(self, allreplays=False):
        """Finds bank folder locations one or more players
        by default check only the last game, if `allreplays` == True, check for all replays"""

        unknown_handles = set(self.main_handles)
        known_handles = dict()
        replays = self.ReplayDataAll if allreplays else self.get_last_replays(1)

        for r in replays:
            if len(unknown_handles) == 0:
                break

            for p in (1, 2):
                if r['players'][p]['handle'] in unknown_handles:
                    unknown_handles.remove(r['players'][p]['handle'])
                    folder = r['file'].split('Replays\\Multiplayer')[0]
                    handle = folder.split('\\')[-2]
                    folder = os.path.join(folder, 'Banks', handle)
                    known_handles[r['players'][p]['handle']] = [r['region'], folder]

        return known_handles

    def analyse_replays(
        self,
        include_mutations=True,
        include_normal_games=True,
        mindate=None,
        maxdate=None,
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
            data = [r for r in data if int(r['date'].replace(':', '')) > mindate]

        if maxdate != None:
            data = [r for r in data if int(r['date'].replace(':', '')) < maxdate]

        if minlength != None:
            data = [r for r in data if r['length'] >= minlength * 60]

        if maxLength != None:
            data = [r for r in data if r['length'] <= maxLength * 60]

        if difficulty_filter != None and len(difficulty_filter) > 0:
            logger.info(f'{difficulty_filter=}')
            for difficulty in difficulty_filter:
                if isinstance(difficulty, str):
                    data = [r for r in data
                            if not difficulty in r['difficulty'] or r['brutal_plus'] > 0]  # Don't filter out B+ if filtering out "Brutal"

                elif isinstance(difficulty, int):
                    data = [r for r in data if not difficulty == r['brutal_plus']]

        if region_filter != None and len(region_filter) > 0:
            logger.info(f'{region_filter=}')
            data = [r for r in data if not r['region'] in region_filter and r['region'] in ('NA', 'EU', 'KR', 'CN')]

        if not sub_15:
            data = [r for r in data if not self.main_player_is_sub_15(r)]

        if not over_15:
            data = [r for r in data if self.main_player_is_sub_15(r)]

        if not include_both_main:
            data = [r for r in data if not self.both_main_players(r)]

        logger.info(f'Filtering {len(self.ReplayData)} -> {len(data)}')

        # Analyse
        DifficultyData = calculate_difficulty_data(data)
        MapData = calculate_map_data(data)
        CommanderData, AllyCommanderData = calculate_commander_data(data, self.main_handles)
        RegionData = calculate_region_data(data, self.main_handles)
        UnitData = None if not self.full_analysis_finished else calculate_unit_stats(data, self.main_handles)

        return {
            'UnitData': UnitData,
            'RegionData': RegionData,
            'DifficultyData': DifficultyData,
            'MapData': MapData,
            'CommanderData': CommanderData,
            'AllyCommanderData': AllyCommanderData,
            'games': len(data)
        }


def mass_replay_analysis_thread(ACCOUNTDIR):
    """ Main thread for mass replay analysis. Handles all initialization. """

    CAnalysis = mass_replay_analysis(ACCOUNTDIR)
    CAnalysis.initialize()
    return CAnalysis