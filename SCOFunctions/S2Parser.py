import os
import mpyq
import json
import time

from s2protocol import versions
from s2protocol.build import game_version as protocol_build
from SCOFunctions.SC2Dictionaries import map_names
from SCOFunctions.MLogging import logclass

logger = logclass('PARS','INFO')

diff_dict = {1:'Casual',2:'Normal',3:'Hard',4:'Brutal'}
region_dict = {1:'NA', 2:'EU', 3:'KR', 5:'CN', 98:'PTR'}
valid_protocols = {81102: 81433, 80871: 81433, 76811: 76114}
protocols = [15405, 16561, 16605, 16755, 16939, 17266, 17326, 18092, 18468, 18574, 19132, 19458, 19595, 19679, 21029, 22612, 23260, 24944, 26490, 27950, 28272, 28667, 32283, 51702, 52910, 53644, 54518, 55505, 55958, 56787, 57507, 58400, 59587, 60196, 60321, 62347, 62848, 63454, 64469, 65094, 65384, 65895, 66668, 67188, 67926, 69232, 70154, 71061, 71523, 71663, 72282, 73286, 73559, 73620, 74071, 74456, 74741, 75025, 75689, 75800, 76052, 76114, 77379, 77535, 77661, 78285, 80669, 80949, 81009, 81433]


def find_closest_values(number:int, llist:list, amount=2):
    """ Finds `amount` of closest numbers in a list to the provided number"""
    closest = {abs(p-number):p for p in llist}
    closest = {k:v for k,v in sorted(closest.items())}
    return list(closest.values())[:amount]


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


def s2_parse_replay(file, try_lastest=True, parse_events=True, onlyBlizzard=False, withoutRecoverEnabled=False, return_raw=False, return_events=False, try_closest=False):
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

    # If the build is in a known list of protocols that aren't included but work, replace the build by the version that works.
    base_build = valid_protocols.get(base_build, base_build)

    try:
        protocol = versions.build(base_build)
        used_build = base_build
    except:
        if try_closest:
            used_build = find_closest_values(base_build, valid_protocols)[0]
            protocol = versions.build(used_build)
        elif try_lastest:
            protocol = versions.latest()
            used_build = protocol_build().split('.')[-2]
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

    # Messages
    messages = archive.read_file('replay.message.events')
    messages = protocol.decode_replay_message_events(messages)

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
    replay['build'] = {'replay_build': base_build, 'protocol_build': used_build}
    replay['date'] = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime(os.path.getmtime(file)))

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
    replay['last_deselect_event'] = replay['last_deselect_event'] if replay['last_deselect_event'] != None else replay['length']
    replay['result'] = 'Victory' if metadata['Players'][0]['Result'] == 'Win' or metadata['Players'][1]['Result'] == 'Win' else 'Defeat'

    if replay['result'] == 'Victory' and parse_events:
        replay['accurate_length'] = replay['last_deselect_event'] - replay['start_time']
        replay['end_time'] = replay['last_deselect_event']
    else:
        replay['accurate_length'] = replay['length'] - replay['start_time']
        replay['end_time'] = replay['length']


    replay['form_alength'] = time.strftime('%H:%M:%S', time.gmtime(replay['accurate_length']))
    replay['form_alength'] = replay['form_alength'] if not replay['form_alength'].startswith('00:') else replay['form_alength'][3:] 

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
        if idx == 0:
            replay['region'] = region_dict.get(player['m_toon']['m_region'],'')

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

    # Messages
    messages = [m for m in messages if m.get('m_string',None) != None]
    replay['messages'] = [{'text':m['m_string'].decode(),'player':m['_userid']['m_userId']+1,'time':m['_gameloop']/16} for m in messages]

    # Events
    if return_events:
        replay['events'] = events

    # Raw
    if return_raw:
        replay['raw'] = {'metadata':metadata, 'player_info': player_info, 'detailed_info': detailed_info}

    return replay