"""
A bit messy module containing functionality responsible for 
sending info to the overlay with socket/JS

Checking for new replays and games. Uploading replays to AOM.
And more.
"""
import os
import json
import time
import threading
import traceback

import requests
import asyncio
import websockets

from SCOFunctions.MLogging import logclass
from SCOFunctions.ReplayAnalysis import analyse_replay
from SCOFunctions.HelperFunctions import get_hash

OverlayMessages = []  # Storage for all messages
globalOverlayMessagesSent = 0  # Global variable to keep track of messages sent. Useful when opening new overlay instances later.
lock = threading.Lock()
logger = logclass('MAIN', 'INFO')
initMessage = {'initEvent': True, 'colors': ['null', 'null', 'null', 'null'], 'duration': 60}
ReplayPosition = 0
AllReplays = dict()
player_winrate_data = dict()
PLAYER_HANDLES = set()  # Set of handles of the main player
PLAYER_NAMES = set()  # Set of names of the main player generated from handles and used in winrate notification
most_recent_playerdata = None
SETTINGS = dict()
CAnalysis = None
APP_CLOSING = False
session_games = {'Victory': 0, 'Defeat': 0}
WEBPAGE = None
RNG_COMMANDER = dict()


def stop_threads():
    """ Sets a variable that lets threads know they should finish early """
    global APP_CLOSING
    APP_CLOSING = True


def update_settings(d):
    """ Through this function the main script passes all its settings here """
    global SETTINGS
    global initMessage

    SETTINGS = d
    initMessage['colors'] = [SETTINGS['color_player1'], SETTINGS['color_player2'], SETTINGS['color_amon'], SETTINGS['color_mastery']]
    initMessage['duration'] = SETTINGS['duration']


def sendEvent(event):
    """ Send message to the overlay """
    global globalOverlayMessagesSent

    with lock:
        # Update global messages. So a new socket doesn't get all previous once at once.
        globalOverlayMessagesSent += 1
        # Websocket connection for non-primary overlay
        OverlayMessages.append(event)

    # Send message directly thorugh javascript for the primary overlay.
    if WEBPAGE == None:
        return

    elif event.get('replaydata') is not None:
        data = json.dumps(event)
        WEBPAGE.runJavaScript(f"postGameStatsTimed({data});")

    elif event.get('mutatordata') is not None:
        data = json.dumps(event)
        WEBPAGE.runJavaScript(f"mutatorInfo({data['data']})")

    elif event.get('hideEvent') is not None:
        WEBPAGE.runJavaScript("hidestats()")

    elif event.get('showEvent') is not None:
        WEBPAGE.runJavaScript("showstats()")

    elif event.get('showHideEvent') is not None:
        WEBPAGE.runJavaScript("showhide()")

    elif event.get('uploadEvent') is not None:
        data = json.dumps(event)
        WEBPAGE.runJavaScript(f"setTimeout(uploadStatus, 1500, '{event['response']}')")

    elif event.get('initEvent') is not None:
        data = json.dumps(event)
        WEBPAGE.runJavaScript(f"initColorsDuration({data})")

    elif event.get('playerEvent') is not None:
        data = json.dumps(event)
        WEBPAGE.runJavaScript(f"showHidePlayerWinrate({data})")


def resend_init_message():
    """ Resends init message. In case duration of colors have changed. """
    sendEvent(initMessage)


def find_names_and_handles(ACCOUNTDIR, replays=None):
    """ Finds player handles and names from the account directory (or its subfolder) """
    # First walk up as far as possible in-case the user has selected one the of subfolders.
    folder = ACCOUNTDIR
    while True:
        parent = os.path.dirname(folder)
        if 'StarCraft' in parent:
            folder = parent
        else:
            break

    # Find handles & names
    handles = set()
    names = set()

    for root, directories, files in os.walk(folder):
        for directory in directories:
            if directory.count(
                    '-') >= 3 and not r'\Banks' in root and not 'Crash' in directory and not 'Desync' in directory and not 'Error' in directory:
                handles.add(directory)

        for file in files:
            if file.endswith('.lnk') and '_' in file and '@' in file:
                names.add(file.split('_')[0])

    # Fallbacks for finding player names: settings, replays, winrates
    if len(names) == 0 and len(SETTINGS['main_names']) > 0:
        names = set(SETTINGS['main_names'])
        logger.info(f'No player names found, falling back to settings: {names}')

    if len(names) == 0 and len(handles) > 0 and replays != None:
        replays = [v.get('replay_dict', {'parser': None}).get('parser', None) for k, v in replays.items() if v != None]
        replays = [r for r in replays if r != None]
        names = names_fallback(handles, replays)
        logger.info(f'No player names found, falling back to replays: {names}')

    if len(names) == 0 and len(player_winrate_data) > 0:
        names = {list(player_winrate_data.keys())[0]}
        logger.info(f'No player names found, falling back to winrate: {names}')

    return names, handles


def names_fallback(handles, replays):
    """ Finds new main player names from handles and replays.Assumes S2Parser format of replays. """
    shandles = set(handles)
    snames = set()

    for r in replays:
        if len(shandles) == 0:
            break
        for p in {1, 2}:
            if r['players'][p]['handle'] in shandles:
                snames.add(r['players'][p]['name'])
                shandles.remove(r['players'][p]['handle'])
    return snames


def update_names_and_handles(ACCOUNTDIR, AllReplays):
    """ Takes player names and handles, and updates global variables with them"""
    global PLAYER_HANDLES
    global PLAYER_NAMES
    names, handles = find_names_and_handles(ACCOUNTDIR, replays=AllReplays)
    if len(handles) > 0:
        logger.info(f'Found {len(handles)} player handles: {handles}')
        with lock:
            PLAYER_HANDLES = handles
    else:
        logger.error('No player handles found!')

    if len(names) > 0:
        logger.info(f'Found {len(names)} player names: {names}')
        with lock:
            PLAYER_NAMES = names
    else:
        logger.error('No player names found!')


def find_replays(directory):
    """ Finds all replays in a directory. Returns a set."""
    replays = set()
    for root, directories, files in os.walk(directory):
        for file in files:
            if file.endswith('.SC2Replay'):
                file_path = os.path.join(root, file)
                if len(file_path) > 255:
                    file_path = '\\\?\\' + file_path
                file_path = os.path.normpath(file_path)
                replays.add(file_path)
    return replays


def initialize_AllReplays(ACCOUNTDIR):
    """ Creates a sorted dictionary of all replays with their last modified times """
    try:
        AllReplays = find_replays(ACCOUNTDIR)
        # Get dictionary of all replays with their last modification time
        AllReplays = ((rep, os.path.getmtime(rep)) for rep in AllReplays)
        AllReplays = {k: {'created': v} for k, v in sorted(AllReplays, key=lambda x: x[1])}
    except:
        logger.error(f'Error during replay initialization\n{traceback.format_exc()}')
    finally:
        return AllReplays


def set_player_winrate_data(winrate_data):
    global player_winrate_data
    with lock:
        player_winrate_data = winrate_data.copy()


def initialize_replays_names_handles():
    """ Checks every few seconds for new replays """
    global AllReplays
    global ReplayPosition

    with lock:
        AllReplays = initialize_AllReplays(SETTINGS['account_folder'])
        logger.info(f'Initializing AllReplays with length: {len(AllReplays)}')
        ReplayPosition = len(AllReplays)

    check_names_handles()
    return None


def check_names_handles():
    try:
        update_names_and_handles(SETTINGS['account_folder'], AllReplays)
    except:
        logger.error(f'Error when finding player handles:\n{traceback.format_exc()}')


def check_replays():
    """ Checks every few seconds for new replays """
    global AllReplays
    global session_games
    global ReplayPosition

    while True:
        logger.debug('Checking for replays....')
        # Check for new replays
        current_time = time.time()
        for root, directories, files in os.walk(SETTINGS['account_folder']):
            for file in files:
                file_path = os.path.join(root, file)
                if len(file_path) > 255:
                    file_path = '\\\?\\' + file_path
                file_path = os.path.normpath(file_path)
                if file.endswith('.SC2Replay') and not (file_path in AllReplays):
                    with lock:
                        AllReplays[file_path] = {'created': os.path.getmtime(file_path)}

                    if current_time - os.path.getmtime(file_path) < 60:
                        logger.info(f'New replay: {file_path}')
                        replay_dict = dict()
                        try:
                            replay_dict = analyse_replay(file_path, PLAYER_HANDLES)

                            # First check if any commander found
                            if not replay_dict.get('mainCommander') and not replay_dict.get('allyCommander'):
                                logger.info('No commanders found, wont show replay')
                            # Then check if we have good
                            elif len(replay_dict) > 1:
                                logger.debug('Replay analysis result looks good, appending...')
                                with lock:
                                    session_games[replay_dict['result']] += 1

                                # What to send
                                out = replay_dict.copy()
                                out['newReplay'] = True
                                if SETTINGS.get('show_session', False):
                                    out.update(session_games)
                                if SETTINGS.get('show_random_on_overlay', False) and len(RNG_COMMANDER) > 0:
                                    out.update(RNG_COMMANDER)
                                if CAnalysis is not None:
                                    out['fastest'] = CAnalysis.check_for_record(replay_dict)

                                sendEvent(out)

                            # No output
                            else:
                                logger.error(f'ERROR: No output from replay analysis ({file})')
                            with lock:
                                ReplayPosition = len(AllReplays) - 1

                        except:
                            logger.error(traceback.format_exc())

                        finally:
                            if len(replay_dict) > 1:
                                upload_to_aom(file_path, replay_dict)
                                # return just parser
                                return replay_dict

        # Wait while checking if the thread should end early
        for i in range(6):
            time.sleep(0.5)
            if APP_CLOSING:
                return None


def upload_to_aom(file_path, replay_dict):
    """ Function handling uploading the replay on the Aommaster's server"""
    # Credentials need to be set up
    if SETTINGS['aom_account'] in {'', None} or SETTINGS['aom_secret_key'] in {'', None}:
        return

    # Never upload old replays
    if (time.time() - os.path.getmtime(file_path)) > 60:
        return

    # Upload only valid non-arcade replays
    if replay_dict.get('mainCommander', None) in [None, ''] or '[MM]' in file_path:
        sendEvent({'uploadEvent': True, 'response': 'Not valid replay for upload'})
        return

    url = f"https://starcraft2coop.com/scripts/assistant/replay.php?username={SETTINGS['aom_account']}&secretkey={SETTINGS['aom_secret_key']}"
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file})
        logger.info(f'Replay upload reponse: {response.text}')

        if 'Success' in response.text or 'Error' in response.text:
            sendEvent({'uploadEvent': True, 'response': response.text})

    except:
        sendEvent({'uploadEvent': True, 'response': 'Error'})
        logger.error(f'Failed to upload replay\n{traceback.format_exc()}')


def show_overlay(file):
    """ Shows overlay. If it wasn't analysed before, analyse now."""
    global ReplayPosition

    if file in AllReplays.keys():
        with lock:
            ReplayPosition = list(AllReplays.keys()).index(file)

    # Try to find if the replay is analysed in CAnalysis
    rhash = get_hash(file)
    if CAnalysis is not None:
        data = CAnalysis.get_data_for_overlay(rhash)
        if data is not None:
            sendEvent(data)
            return

    # Didn't find the replay, analyse
    try:
        replay_dict = analyse_replay(file, PLAYER_HANDLES)
        if len(replay_dict) > 1:
            sendEvent(replay_dict)
            if CAnalysis is not None:
                CAnalysis.add_parsed_replay(replay_dict)
        else:
            logger.error('No output from replay analysis')
    except:
        logger.error(f'Failed to analyse replay: {file}\n{traceback.format_exc()}')
        return 'Error'
        

async def manager(websocket, path):
    """ Manages websocket connection for each client """
    overlayMessagesSent = globalOverlayMessagesSent
    logger.info(f"Starting: {websocket}\nSending init message: {initMessage}")
    await websocket.send(json.dumps(initMessage))
    while True:
        try:
            if len(OverlayMessages) > overlayMessagesSent:
                message = json.dumps(OverlayMessages[overlayMessagesSent])
                overlayMessagesSent += 1
                logger.info(f'#{overlayMessagesSent-1} message is being sent through {websocket}')

                try:  # Send the message
                    await asyncio.wait_for(asyncio.gather(websocket.send(message)), timeout=1)
                except asyncio.TimeoutError:
                    logger.error(f'#{overlayMessagesSent-1} message was timed-out.')
                except websockets.exceptions.ConnectionClosedOK:
                    logger.info('Websocket connection closed (ok).')
                    break
                except websockets.exceptions.ConnectionClosedError:
                    logger.info('Websocket connection closed (error).')
                    break
                except websockets.exceptions.ConnectionClosed:
                    logger.info('Websocket connection closed.')
                    break
                except:
                    logger.error(traceback.format_exc())
        except:
            logger.error(traceback.format_exc())
        finally:
            await asyncio.sleep(0.1)


def server_thread(PORT=7305):
    """ Creates a websocket server """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_server = websockets.serve(manager, 'localhost', PORT)
        logger.info('Starting websocket server')
        loop.run_until_complete(start_server)
        loop.run_forever()
    except:
        logger.error(traceback.format_exc())


def move_in_AllReplays(delta):
    """ Moves across all replays and sends info to overlay to show parsed data """
    global ReplayPosition
    logger.info(f'Attempt to move to {ReplayPosition + delta}/{len(AllReplays)-1}')

    # Check if valid position
    newPosition = ReplayPosition + delta
    if newPosition < 0 or newPosition >= len(AllReplays):
        logger.info(f'We have gone too far. Staying at {ReplayPosition}')
        return

    # Get replay_dict of given replay
    file = list(AllReplays.keys())[newPosition]
    result = show_overlay(file)
    if result == 'Error':
        move_in_AllReplays(delta)


def keyboard_OLDER():
    """ Show older replay"""
    move_in_AllReplays(-1)


def keyboard_NEWER():
    """ Show newer replay"""
    move_in_AllReplays(1)


def keyboard_SHOWHIDE():
    """ Show/hide overlay"""
    logger.info('Show-Hide event')
    sendEvent({'showHideEvent': True})


def keyboard_HIDE():
    """ Hide overlay """
    logger.info('Hide event')
    sendEvent({'hideEvent': True})


def keyboard_SHOW():
    """ Show overlay """
    logger.info('Show event')
    sendEvent({'showEvent': True})


def keyboard_PLAYERWINRATES():
    """Show/hide winrate & notes """
    if most_recent_playerdata:
        logger.info(f'Player Winrate key triggered, sending player data event: {most_recent_playerdata}')
        sendEvent({'playerEvent': True, 'data': most_recent_playerdata})
    else:
        logger.info(f'Could not send player data event since most_recent_playerdata was: {most_recent_playerdata}')


def wait_for_wake():
    """
    The goal of this function is to detect when a PC was awaken from sleeping.
    It will be checking time, and if there is a big discrepancy, it will return it.
    This function will be run on a separate thread.
    """
    while True:
        start = time.time()

        # Wait 5s
        for i in range(20):
            time.sleep(0.5)
            if APP_CLOSING:
                return None

        # Check the difference
        diff = time.time() - start
        if diff > 20:
            return diff - 10


def check_for_new_game():
    global most_recent_playerdata
    """ Thread checking for a new game and sending signals to the overlay with player winrate stats"""
    # Wait a bit for the replay initialization to complete
    time.sleep(4)
    """
    To identify new game, this is checking for the ingame display time to change. Plus isReplay has to be False.
    To identify unique new game, we want the length of all replays to change first => new game.
    And we don't want to show it right after all replays changed, since that's a false positive and ingame time actually didn't change.

    """
    last_game_time = None
    last_replay_amount = 0
    last_replay_amount_flowing = len(AllReplays)  # This helps identify when a replay has been parsed
    last_replay_time = 0  # Time when we got the last replay parsed

    while True:
        time.sleep(0.5)

        if APP_CLOSING:
            break

        # Skip if winrate data not showing OR no new replay analysed, meaning it's the same game (excluding the first game)
        if len(player_winrate_data) == 0 or len(AllReplays) == last_replay_amount:
            continue

        # When we get a new replay, mark the time
        if len(AllReplays) > last_replay_amount_flowing:
            last_replay_amount_flowing = len(AllReplays)
            last_replay_time = time.time()

        try:
            # Request player data from the game
            resp = requests.get('http://localhost:6119/game', timeout=6).json()
            players = resp.get('players', list())

            # Don't show in if all players are type user - versus game
            all_users = True
            for player in players:
                if player['type'] != 'user':
                    all_users = False

            if all_users:
                continue

            # Check if we have players in, and it's not a replay
            if len(players) > 2 and not resp.get('isReplay', True):
                # If the last time is the same, then we are in menus. Otherwise in-game.

                if last_game_time == None or resp['displayTime'] == 0:
                    last_game_time = resp['displayTime']
                    continue

                if last_game_time == resp['displayTime']:
                    logger.debug(f"The same time (curent: {resp['displayTime']}) (last: {last_game_time}) skipping...")
                    continue

                last_game_time = resp['displayTime']

                # Don't show too soon after a replay has been parsed, false positive.
                if time.time() - last_replay_time < 15:
                    logger.debug('Replay added recently, wont show player winrates right now')
                    continue

                # Mark this game so it won't be checked it again
                last_replay_amount = len(AllReplays)

                # Add the first player name that's not the main player. This could be expanded to any number of players.
                if len(PLAYER_NAMES) > 0:
                    test_names_against = [p.lower() for p in PLAYER_NAMES]
                elif len(SETTINGS['main_names']) > 0:
                    test_names_against = [p.lower() for p in SETTINGS['main_names']]
                else:
                    logger.error('No main names to test against')
                    continue

                player_names = set()
                for player in players:
                    if player['id'] in {1, 2} and not player['name'].lower() in test_names_against and player['type'] != 'computer':
                        player_names.add(player['name'])
                        break

                # If we have players to show
                if len(player_names) > 0:
                    # Get player winrate data
                    data = {p: player_winrate_data.get(p, [None]) for p in player_names}
                    # Get player notes
                    for player in data:
                        if player in SETTINGS['player_notes']:
                            data[player].append(SETTINGS['player_notes'][player])

                    most_recent_playerdata = data
                    logger.info(f'Sending player data event: {data}')
                    sendEvent({'playerEvent': True, 'data': data})

        except requests.exceptions.ConnectionError:
            logger.debug(f'SC2 request failed. Game not running.')

        except json.decoder.JSONDecodeError:
            logger.info('SC2 request json decoding failed (SC2 is starting or closing)')

        except requests.exceptions.ReadTimeout:
            logger.info('SC2 request timeout')

        except:
            logger.info(traceback.format_exc())