import mpyq
import json

from s2protocol import versions


def get_last_deselect_event(events):
    """ Returns the last deselect event in replay's events """
    last_event = 0
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


def s2_parse_replay(file, return_raw=False, return_events=False):
    """ Function parsing the replay and returning a replay class

    'raw'=True returns raw data as well"""

    archive = mpyq.MPQArchive(file)
    contents = archive.header['user_data_header']['content']

    header = versions.latest().decode_replay_header(contents)
    base_build = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(base_build)
    except:
        protocol = versions.latest()
    

    # Get game events
    game_events = archive.read_file('replay.game.events')
    game_events = protocol.decode_replay_game_events(game_events)  

    # Get tracker events
    tracker_events = archive.read_file('replay.tracker.events')
    tracker_events = protocol.decode_replay_tracker_events(tracker_events) 

    # Merge them together
    events = list(game_events) + list(tracker_events)
    events = sorted(events, key=lambda x:x['_gameloop'])

    # Get player info
    player_info = archive.read_file('replay.details')
    player_info = protocol.decode_replay_details(player_info)

    # Get detailed info
    detailed_info = archive.read_file('replay.initData')
    detailed_info = protocol.decode_replay_initdata(detailed_info)

    # Get metadata
    metadata = json.loads(archive.read_file('replay.gamemetadata.json'))

    ##########################

    replay = dict()
    replay['map_name'] = metadata['Title']
    replay['isBlizzard'] = player_info['m_isBlizzardMap']
    replay['extension'] = detailed_info['m_syncLobbyState']['m_gameDescription']['m_hasExtensionMod']
    replay['brutal_plus'] = detailed_info['m_syncLobbyState']['m_lobbyState']['m_slots'][0].get('m_brutalPlusDifficulty',0)
    replay['length'] = metadata['Duration']
    replay['start_time'] = get_start_time(events)
    replay['last_deselect_event'] = get_last_deselect_event(events)
    replay['result'] = 'Victory' if metadata['Players'][0]['Result'] == 'Win' or metadata['Players'][1]['Result'] == 'Win' else 'Defeat'

    if replay['result'] == 'Victory':
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

    for idx,player in enumerate(detailed_info['m_syncLobbyState']['m_lobbyState']['m_slots']):
        if idx < len(replay['players']):
            replay['players'][idx]['masteries'] = player['m_commanderMasteryTalents']
            replay['players'][idx]['commander'] = player['m_commander'].decode()
            replay['players'][idx]['commander_level'] = player['m_commanderLevel']
            replay['players'][idx]['commander_mastery_level'] = player['m_commanderMasteryLevel']
            replay['players'][idx]['prestige'] = player.get('m_selectedCommanderPrestige',0)
            replay['players'][idx]['handle'] = player['m_toonHandle'].decode()
            replay['players'][idx]['difficulty'] = player['m_difficulty']

    for idx,player in enumerate(detailed_info['m_syncLobbyState']['m_userInitialData']):
        _name = player['m_name'].decode()
        if idx < len(replay['players']) and _name != '':
            replay['players'][idx]['name'] = _name

    # Insert dummy players to positions: zero & two if playing alone.
    replay['players'].insert(0, {'pid':0})
    if replay['players'][2]['pid'] != 2:
        replay['players'].insert(2, {'pid':2})

    # Difficulty
    replay['difficulty'] = (replay['players'][3]['difficulty'],replay['players'][4]['difficulty'])
    for player in replay['players']: # Delete difficulty per player as it's not accurate for human players and we are returning map difficulty already
        player.pop('difficulty', None)

    # Events
    if return_events:
        replay['events'] = events

    # Raw
    if return_raw:
        replay['raw'] = [metadata, player_info, detailed_info]

    return replay


# DEBUGGING
if __name__ == '__main__':
    from pprint import pprint   
    file_path = r'C:\\Users\\Maguro\\Documents\\StarCraft II\\Accounts\\114803619\\1-S2-1-4189373\\Replays\\Multiplayer\\[MM] Temple of the Past - Terran (22).SC2Replay'
    replay = s2_parse_replay(file_path)
    pprint(replay)
