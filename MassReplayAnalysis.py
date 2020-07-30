import os
import mpyq
import json
import traceback
from pprint import pprint

from s2protocol import versions
from MLogging import logclass

logger = logclass('SCOM','INFO')


def get_player_stats(file, archive=None):
    """ Returns players and game results for given replay"""

    if archive == None:
        archive = mpyq.MPQArchive(file) # Passing already opened archive inside 

    contents = archive.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)
    base_build = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(base_build)
    except:
        protocol = versions.latest()

    try:
        details = archive.read_file('replay.details')
        details = protocol.decode_replay_details(details)

        # Get stats only for Blizzard maps, and recover replay has to be disabled (live Co-op)
        if details['m_isBlizzardMap'] == False or details['m_disableRecoverGame'] == False:
            return [None,'Win'],[None,'Win']

        # Get names
        p1 = details['m_playerList'][0]['m_name'].decode().split('<sp/>')[-1]
        p2 = None
        if len(details['m_playerList']) > 1:
            p2 = details['m_playerList'][1]['m_name'].decode().split('<sp/>')[-1]

        # Get results
        metadata = json.loads(archive.read_file('replay.gamemetadata.json'))
        result = 'Loss'
        if metadata['Players'][0]['Result'] == 'Win':
            result = 'Win'
        elif len(metadata['Players']) > 1 and metadata['Players'][1]['Result'] == 'Win':
            result = 'Win'

        return [p1,result],[p2,result]
    except:
        logger.error(f'Failed to parse: {file}')
        return [None,'Win'],[None,'Win']


def calculate_player_stats(replays):
    """ Counts wins and losses for all players (1,2) in given replays """

    # Analyse
    games = map(get_player_stats, replays)

    # Calculate wins, losses and exclude some player names
    excluded = {None,'Purifier Hologram',"Amon's Forces", 'Forces of Amon'}
    games = [g for game in games for g in game if not g[0] in excluded] # Unpack list of lists
    wins = [game[0] for game in games if game[1]=='Win']
    losses = [game[0] for game in games if game[1]=='Loss']
    players = {game[0]:[wins.count(game[0]),losses.count(game[0])] for game in games} # Count losses and wins

    return players


def get_player_winrates(AllReplays, save_file=True):
    """ Returns winrate data. Uses saved data if available. Saves data by default."""
        
    players = {}
    file_modified = 0

    if os.path.isfile('PlayerWinrates.json'):
        try:
            # Get time of saved data
            file_modified = os.path.getmtime('PlayerWinrates.json')
            # Parse saved data
            with open('PlayerWinrates.json', 'r') as f:
                players = json.load(f)[1]
        except:
            file_modified = 0
            logger.error(traceback.format_exc())

    
    # Exclude MM replays
    AllReplays = {r:AllReplays[r] for r in AllReplays if not '[MM]' in r}

    # Parse replays newer than the file
    new_replays = {r:AllReplays[r] for r in AllReplays if AllReplays[r]['created'] > file_modified}
    new_player_data = calculate_player_stats(new_replays)
    logger.info(f'Appending {len(new_player_data)} players with new winrate data')

    # Append
    for player in new_player_data:
        if player in players:
            players[player][0] += new_player_data[player][0]
            players[player][1] += new_player_data[player][1]
        else:
            players[player] = new_player_data[player]

    # Sort    
    players = {k:v for k,v in sorted(players.items(), key=lambda x:x[1][0], reverse=True)} 

    # Save 
    if save_file:
        with open('PlayerWinrates.json', 'w') as f:
            data = [{'name':['wins','losses']},players]
            json.dump(data, f, indent=2)

    return players

