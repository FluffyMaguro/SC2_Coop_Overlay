import os
import mpyq
import json
from datetime import datetime

from s2protocol import versions
from SCOFunctions.SC2Dictionaries import map_names
from SCOFunctions.MLogging import logclass

logger = logclass('PARS','INFO')

diff_dict = {1:'Casual',2:'Normal',3:'Hard',4:'Brutal'}


def get_last_deselect_event(events):
    """ Returns the last deselect event in replay's events """
    last_event = None
    for event in events:
        if event['_event'] == 'NNet.Game.SSelectionDeltaEvent':
            last_event = event['_gameloop']/16 - 2 #16 gameloops per second, offset to coincide with speedrun timings more

    return last_event


def get_start_time(events):
    """ Returns accurate start time based on upgrades and mineral collection as fallback"""
    for event in events:
        if event['_event'] == 'NNet.Replay.Tracker.SPlayerStatsEvent' and event['m_playerId'] == 1 and event['m_stats']['m_scoreValueMineralsCollectionRate'] > 0:
            return event['_gameloop']/16
        if event['_event'] == 'NNet.Replay.Tracker.SUpgradeEvent' and event['m_playerId'] in [1,2] and 'Spray' in event['m_upgradeTypeName'].decode():
            return event['_gameloop']/16
    return 0


def s2_parse_replay(file, try_lastest=True, parse_events=True, onlyBlizzard=False, withoutRecoverEnabled=False, return_raw=False, return_events=False):
    """ Function parsing the replay and returning a replay class

    `try_lastest=False` doesn't try the lastest protocol version
    `parse_events = False` prevents parsing replay events, less accurate game length
    `onlyBlizzard = True` returns `None` for non-blizzard replays. Commanders have to be found.
    `withoutRecoverEnabled = True` returns `None` for games with game recovery enabled
    `return_raw = True` returns raw data as well
    `return_events = True` returns events as well
    """

    # Exit straight away if onlyBlizzard enforced
    if onlyBlizzard and '[MM]' in file:
        return None 

    # Open archive
    archive = mpyq.MPQArchive(file)
    contents = archive.header['user_data_header']['content']

    header = versions.latest().decode_replay_header(contents)
    base_build = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(base_build)
    except:
        if try_lastest:
            protocol = versions.latest()
            logger.info('Trying the lastest protocol')
        else:
            return None

    # Get player info
    player_info = archive.read_file('replay.details')
    player_info = protocol.decode_replay_details(player_info)

    # Exit if onlyBlizzard maps enforced
    if onlyBlizzard and not player_info['m_isBlizzardMap']:
        return None

    # Exit if game can be recovered
    if withoutRecoverEnabled and not player_info['m_disableRecoverGame']:
        return None

    # Get detailed info
    detailed_info = archive.read_file('replay.initData')
    detailed_info = protocol.decode_replay_initdata(detailed_info)

    # Get metadata
    metadata = json.loads(archive.read_file('replay.gamemetadata.json'))

    events = list()
    if parse_events:
        # Get game events
        game_events = archive.read_file('replay.game.events')
        game_events = protocol.decode_replay_game_events(game_events)  

        # Get tracker events
        tracker_events = archive.read_file('replay.tracker.events')
        tracker_events = protocol.decode_replay_tracker_events(tracker_events) 

        # Merge them together
        events = list(game_events) + list(tracker_events)
        events = sorted(events, key=lambda x:x['_gameloop'])

    # Create output
    replay = dict()
    replay['file'] = file
    replay['date'] = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y:%m:%d:%H:%M:%S")

    if metadata['Title'] in map_names:
        replay['map_name'] = map_names[metadata['Title']]['EN']
    else:
        replay['map_name'] = metadata['Title']

    replay['isBlizzard'] = player_info['m_isBlizzardMap']
    replay['extension'] = detailed_info['m_syncLobbyState']['m_gameDescription']['m_hasExtensionMod']
    replay['brutal_plus'] = detailed_info['m_syncLobbyState']['m_lobbyState']['m_slots'][0].get('m_brutalPlusDifficulty',0)
    replay['length'] = metadata['Duration']
    replay['start_time'] = get_start_time(events)
    replay['last_deselect_event'] = get_last_deselect_event(events)
    replay['result'] = 'Victory' if metadata['Players'][0]['Result'] == 'Win' or metadata['Players'][1]['Result'] == 'Win' else 'Defeat'

    if replay['result'] == 'Victory' and parse_events:
        replay['accurate_length'] = replay['last_deselect_event'] - replay['start_time']
        replay['end_time'] = replay['last_deselect_event']
    else:
        replay['accurate_length'] = replay['length'] - replay['start_time']
        replay['end_time'] = replay['length']

    # Add data to players
    replay['players'] = list()
    for idx,player in enumerate(metadata['Players']):
        p = {'apm':player['APM'],'result':player['Result'],'pid':player['PlayerID']}
        p['apm'] = round(p['apm'] * replay['length'] / replay['accurate_length'])
        replay['players'].append(p)

    for idx,player in enumerate(player_info['m_playerList']):
        replay['players'][idx]['name'] = player['m_name'].decode()
        replay['players'][idx]['race']  = player['m_race'].decode()
        replay['players'][idx]['observer']  = False if player['m_observe'] == 0 else True

    commander_found = False
    for idx,player in enumerate(detailed_info['m_syncLobbyState']['m_lobbyState']['m_slots']):
        if idx < len(replay['players']):
            replay['players'][idx]['masteries'] = player['m_commanderMasteryTalents']
            replay['players'][idx]['commander'] = player['m_commander'].decode()
            replay['players'][idx]['commander_level'] = player['m_commanderLevel']
            replay['players'][idx]['commander_mastery_level'] = player['m_commanderMasteryLevel']
            replay['players'][idx]['prestige'] = player.get('m_selectedCommanderPrestige',0)
            replay['players'][idx]['handle'] = player['m_toonHandle'].decode()
            replay['players'][idx]['difficulty'] = player['m_difficulty']

            if not replay['players'][idx]['commander'] in {None,''}:
                commander_found = True

    # Exit if onlyBlizzard maps enforced
    if onlyBlizzard and not commander_found:
        return None

    # Player names
    for idx,player in enumerate(detailed_info['m_syncLobbyState']['m_userInitialData']):
        _name = player['m_name'].decode()
        if idx < len(replay['players']) and _name != '':
            replay['players'][idx]['name'] = _name

    # Insert dummy players to positions: zero & two if playing alone.
    replay['players'].insert(0, {'pid':0})
    if replay['players'][2]['pid'] != 2:
        replay['players'].insert(2, {'pid':2})

    # Enemy race
    replay['enemy_race'] = replay['players'][3]['race']

    # Difficulty
    diff_1 = diff_dict.get(replay['players'][3]['difficulty'],'')
    diff_2 = diff_dict.get(replay['players'][4]['difficulty'],'')
    replay['difficulty'] = (diff_1,diff_2)

    # Delete difficulty per player as it's not accurate for human players and we are returning map difficulty already
    for player in replay['players']: 
        player.pop('difficulty', None)

    # Extended difficulty (including B+)
    if replay['brutal_plus'] > 0:
        replay['ext_difficulty'] = f'B+{replay["brutal_plus"]}'
    elif diff_1 == diff_2:
        replay['ext_difficulty'] = diff_1
    else:
        replay['ext_difficulty'] = f'{diff_1}/{diff_2}'

    # Events
    if return_events:
        replay['events'] = events

    # Raw
    if return_raw:
        replay['raw'] = {'metadata':metadata, 'player_info': player_info, 'detailed_info': detailed_info}

    return replay