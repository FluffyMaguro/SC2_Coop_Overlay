import os
import json
import time
import threading
import traceback

import requests
import asyncio
import keyboard
import websockets

from MLogging import logclass
from ReplayAnalysis import analyse_replay
from MassReplayAnalysis import get_player_winrates


OverlayMessages = [] # Storage for all messages
globalOverlayMessagesSent = 0 # Global variable to keep track of messages sent. Useful when opening new overlay instances later.
lock = threading.Lock()
logger = logclass('SCOF','INFO')
initMessage = {'initEvent':True,'colors':['null','null','null','null'],'duration':60}
analysis_log_file = 'SCO_analysis_log.txt'
ReplayPosition = 0
AllReplays = dict()
player_winrate_data = dict()
PLAYER_NAMES = []
CONFIG_PLAYER_NAMES = []


def set_initMessage(colors,duration,unifiedhotkey):
    """ Modify init message that's sent to new websockets """
    global initMessage
    initMessage['colors'] = colors
    initMessage['duration'] = duration
    initMessage['unifiedhotkey'] = 'true' if unifiedhotkey else 'false'


def sendEvent(event):
    """ Adds event to messages ready to be sent """
    with lock:
        OverlayMessages.append(event) 


def set_PLAYER_NAMES(names):
    """ Extends global player names variable """
    global PLAYER_NAMES
    global CONFIG_PLAYER_NAMES
    with lock:
        PLAYER_NAMES.extend(names)
        CONFIG_PLAYER_NAMES.extend(names)


def guess_PLAYER_NAMES():
    """ If no PLAYER_NAMES are set, take the best guess for the preferred player"""
    global PLAYER_NAMES

    if len(PLAYER_NAMES) > 0:
        return 

    # If we have calculated winrate data for all players, use that. Otherwise check for common players in analysis log.
    if len(player_winrate_data) > 10:
        with lock:
            PLAYER_NAMES = list(player_winrate_data.keys())[0:3] 
        logger.info(f'Player guess through player_winrate_data: {PLAYER_NAMES}')
        return

    # Get all players to the list
    list_of_players = list()
    for replay in AllReplays:
        replay_dict = AllReplays[replay].get('replay_dict',dict())
        list_of_players.append(replay_dict.get('main',None))
        list_of_players.append(replay_dict.get('ally',None))

    # Remove nones, sort
    players = {i:list_of_players.count(i) for i in list_of_players if not i in [None,'None']} #get counts
    players = {k:v for k,v in sorted(players.items(),key=lambda x:x[1],reverse=True)} #sort

    if len(players) == 0:
        return

    # Get the three most common names. Replay analysis will check from the first one to the last one if they are ingame.
    with lock:
        PLAYER_NAMES = list(players.keys())[0:3] 
    logger.info(f'Player guess through analysis log: {PLAYER_NAMES}')


def initialize_AllReplays(ACCOUNTDIR):
    """ Creates a sorted dictionary of all replays with their last modified times """
    AllReplays = set()
    try:
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                if file.endswith('.SC2Replay'):
                    file_path = os.path.join(root,file)
                    if len(file_path) > 255:
                        file_path = '\\\?\\' + file_path
                    file_path = file_path = os.path.normpath(file_path)
                    AllReplays.add(file_path)

        # Get dictionary of all replays with their last modification time
        AllReplays = ((rep,os.path.getmtime(rep)) for rep in AllReplays)
        AllReplays = {k:{'created':v} for k,v in sorted(AllReplays,key=lambda x:x[1])}

        # Append data from already parsed replays
        if os.path.isfile(analysis_log_file):
            with open(analysis_log_file,'rb') as file:
                for line in file.readlines():
                    try:
                        replay_dict = eval(line.decode('utf-8'))
                        if 'replaydata' in replay_dict and 'filepath' in replay_dict:
                            if replay_dict['filepath'] in AllReplays:
                                AllReplays[replay_dict['filepath']]['replay_dict'] = replay_dict
                    except:
                        print("Failed to parse a line from replay analysis log\n",traceback.format_exc())

    except:
        logger.error(f'Error during replay initialization\n{traceback.format_exc()}')
    finally:
        return AllReplays


def update_player_winrate_data(replay_dict):
    """ Updates global player_winrate_data with new results"""
    global player_winrate_data

    result = replay_dict.get('result',None)
    if result == None:
        return
    elif result == 'Victory': # In player_data, victory are on index 0 and losses on index 1
        result = 0
    else:
        result = 1

    main = replay_dict.get('main',None)
    ally = replay_dict.get('ally',None)

    for player in [main,ally]:
        with lock:
            if not player in player_winrate_data:
                player_winrate_data[player] = [0,0]
            player_winrate_data[player][result] += 1


def check_replays(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY,PLAYER_WINRATES):
    """ Checks every few seconds for new replays """
    global AllReplays
    global ReplayPosition
    global player_winrate_data

    session_games = {'Victory':0,'Defeat':0}

    with lock:
        AllReplays = initialize_AllReplays(ACCOUNTDIR)
        logger.info(f'Initializing AllReplays with length: {len(AllReplays)}')
        ReplayPosition = len(AllReplays)


    if PLAYER_WINRATES:
        try:
            time_counter_start = time.time()
            logger.info(f'Starting mass replay analysis')
            player_winrate_data_temp = get_player_winrates(AllReplays)
            with lock:
                player_winrate_data = player_winrate_data_temp
            logger.info(f'Mass replay analysis completed in {time.time()-time_counter_start:.1f} seconds')
        except:
            logger.error(f'Error when initializing player winrate data:\n{traceback.format_exc()}')

    try:
        guess_PLAYER_NAMES()
    except:
        logger.error(f'Error when guessing player names:\n{traceback.format_exc()}')

    while True:
        logger.debug('Checking for replays....')
        # Check for new replays
        current_time = time.time()
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                file_path = os.path.join(root,file)
                if len(file_path) > 255:
                    file_path = '\\\?\\' + file_path
                if file.endswith('.SC2Replay') and not(file_path in AllReplays): 
                    with lock:
                        AllReplays[file_path] = {'created':os.path.getmtime(file_path)}

                    if current_time - os.path.getmtime(file_path) < 60: 
                        logger.info(f'New replay: {file_path}')
                        replay_dict = dict()
                        try:   
                            replay_dict = analyse_replay(file_path,PLAYER_NAMES)

                            # Good output
                            if len(replay_dict) > 1:
                                logger.debug('Replay analysis result looks good, appending...')
                                session_games[replay_dict['result']] += 1
                                update_player_winrate_data(replay_dict)
                                    
                                sendEvent({**replay_dict,**session_games})
                                with open(analysis_log_file, 'ab') as file: #save into a text file
                                    file.write((str(replay_dict)+'\n').encode('utf-8'))     
                            # No output                         
                            else:
                                logger.error(f'ERROR: No output from replay analysis ({file})')

                            with lock:
                                AllReplays[file_path]['replay_dict'] = replay_dict
                                ReplayPosition = len(AllReplays)-1
                
                        except:
                            logger.error(traceback.format_exc())

                        finally:
                            upload_to_aom(file_path,AOM_NAME,AOM_SECRETKEY,replay_dict)
                            break

        time.sleep(3)   


def upload_to_aom(file_path,AOM_NAME,AOM_SECRETKEY,replay_dict):
    """ Function handling uploading the replay on the Aommaster's server"""

    # Credentials need to be set up
    if AOM_NAME == None or AOM_SECRETKEY == None:
        return

    # Never upload old replays
    if (time.time() - os.path.getmtime(file_path)) > 60:
        return

    # Upload only valid non-arcade replays
    if replay_dict.get('mainCommander',None) in [None,''] or '[MM]' in file_path:
        sendEvent({'uploadEvent':True,'response':'Not valid replay for upload'})
        return

    url = f'https://starcraft2coop.com/scripts/assistant/replay.php?username={AOM_NAME}&secretkey={AOM_SECRETKEY}'
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file})
        logger.info(f'Replay upload reponse: {response.text}')
     
        if 'Success' in response.text or 'Error' in response.text:
            sendEvent({'uploadEvent':True,'response':response.text})
    
    except:
        sendEvent({'uploadEvent':True,'response':'Error'})
        logger.error(f'Failed to upload replay\n{traceback.format_exc()}')


def update_global_overlay_messages(overlayMessagesSent):
    """ Updates global overlay messages to the last value

    This is so a newly opened instance of the overlay won't be sent all previous messages at once"""
    global globalOverlayMessagesSent
    if overlayMessagesSent > globalOverlayMessagesSent:
        with lock:
            globalOverlayMessagesSent = overlayMessagesSent


async def manager(websocket, path):
    """ Manages websocket connection for each client """
    overlayMessagesSent = globalOverlayMessagesSent
    logger.info(f"Starting: {websocket}\nSending init message: {initMessage}")
    await websocket.send(json.dumps(initMessage))
    while True:
        try:
            if len(OverlayMessages) > overlayMessagesSent:
                message = json.dumps(OverlayMessages[overlayMessagesSent])
                logger.info(f'#{overlayMessagesSent} message is being sent through {websocket}')
                overlayMessagesSent += 1
                update_global_overlay_messages(overlayMessagesSent)

                try: # Send the message
                    await asyncio.wait_for(asyncio.create_task(websocket.send(message)), timeout=1)
                    logger.info(f'#{overlayMessagesSent-1} message sent')

                except asyncio.TimeoutError:
                    logger.error(f'#{overlayMessagesSent-1} message was timed-out.')
                except websockets.exceptions.ConnectionClosedOK:
                    logger.error('Websocket connection closed OK!')
                    break
                except websockets.exceptions.ConnectionClosedError:
                    logger.error('Websocket connection closed ERROR!')
                    break            
                except websockets.exceptions.ConnectionClosed:
                    logger.error('Websocket connection closed!')
                    break 
                except:
                    logger.error(traceback.format_exc())

        except:
            logger.error(traceback.format_exc())
        finally:
            await asyncio.sleep(0.1)


def server_thread(PORT):
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

    with lock:
        ReplayPosition = newPosition

    # Get replay_dict of given replay
    key = list(AllReplays.keys())[ReplayPosition]
    if 'replay_dict' in AllReplays[key]:
        if AllReplays[key]['replay_dict'] != None:
            sendEvent(AllReplays[key]['replay_dict'])
        else:
            logger.info(f"This replay couldn't be analysed {key}")
            move_in_AllReplays(delta)
    else:
        # Replay_dict is missing, analyse replay
        try: 
            replay_dict = analyse_replay(key,PLAYER_NAMES)
            if len(replay_dict) > 1:
                sendEvent(replay_dict)
                with lock:
                    AllReplays[key]['replay_dict'] = replay_dict
                with open(analysis_log_file, 'ab') as file:
                    file.write((str(replay_dict)+'\n').encode('utf-8'))  
            else:
                # No output from analysis
                with lock:
                    AllReplays[key]['replay_dict'] = None
                move_in_AllReplays(delta)
        except:
            logger.error(f'Failed to analyse replay: {key}\n{traceback.format_exc()}')
            with lock:
                AllReplays[key]['replay_dict'] = None
            move_in_AllReplays(delta)


def keyboard_thread_OLDER(OLDER):
    """ Thread waiting for hotkey for showing older replay"""
    logger.info('Starting keyboard older thread')
    while True:
        keyboard.wait(OLDER)
        move_in_AllReplays(-1)
        

def keyboard_thread_NEWER(NEWER):
    """ Thread waiting for hotkey for showing newer replay"""
    logger.info('Starting keyboard newer thread')
    while True:
        keyboard.wait(NEWER)
        move_in_AllReplays(1)


def keyboard_thread_HIDE(HIDE):
    """ Thread waiting for hide hotkey """
    logger.info('Starting keyboard hide thread')
    while True:
        keyboard.wait(HIDE)
        logger.info('Hide event')
        sendEvent({'hideEvent': True})


def keyboard_thread_SHOW(SHOW):
    """ Thread waiting for show hotkey """
    logger.info('Starting keyboard show thread')
    while True:
        keyboard.wait(SHOW)
        logger.info('Show event')
        sendEvent({'showEvent': True})


def check_for_new_game(PLAYER_NOTES):
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
    last_replay_amount_flowing = len(AllReplays) # This helps identify when a replay has been parsed
    last_replay_time = 0 # Time when we got the last replay parsed

    while True:
        time.sleep(0.5)
        # Skip if winrate data not showing OR no new replay analysed, meaning it's the same game (excluding the first game)
        if len(player_winrate_data) == 0 or len(AllReplays) == last_replay_amount:
            continue

        # When we get a new replay, mark the time
        if len(AllReplays) > last_replay_amount_flowing:
            last_replay_amount_flowing = len(AllReplays)
            last_replay_time = time.time()

        try:
            # Request player data from the game
            resp = requests.get('http://localhost:6119/game', timeout=4).json()
            players = resp.get('players',list())
            
            # Check if we have players in, and it's not a replay
            if len(players) > 0 and not resp.get('isReplay',True):
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
                player_names = set()
                for player in players:
                    if player['id'] in {1,2} and not player['name'].lower() in [p.lower() for p in CONFIG_PLAYER_NAMES] + [PLAYER_NAMES[0].lower()]:
                        player_names.add(player['name'])
                        break

                # If we have players to show
                if len(player_names) > 0:
                    # Get player winrate data
                    data = {p:player_winrate_data.get(p,[None]) for p in player_names} 
                    # Get player notes
                    for player in data:
                        if player.lower() in PLAYER_NOTES:
                            data[player].append(PLAYER_NOTES[player.lower()])
                            
                    sendEvent({'playerEvent': True,'data':data})
                    logger.info(f'Sending player data event: {data}')


        except requests.exceptions.ConnectionError:
            logger.info(f'SC2 request failed. Game not running.')

        except json.decoder.JSONDecodeError:
            logger.info('SC2 request json decoding failed (SC2 is starting or closing)')

        except requests.exceptions.ReadTimeout:
            logger.info('SC2 request timeout')

        except:
            logger.info(traceback.format_exc())
        
