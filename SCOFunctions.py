import os
import json
import time
import requests
import threading
import traceback
import asyncio
import keyboard
import websockets
from ReplayAnalysis import analyse_replay
from MLogging import logclass

### Storage for all messages
OverlayMessages = []
lock = threading.Lock()
logger = logclass('SCOF','INFO')
initMessage = {'initEvent':True,'colors':['null','null','null','null'],'duration':60}
analysis_log_file = 'SCO_analysis_log.txt'
ReplayPosition = 0
AllReplays = dict()
PLAYER_NAMES = []


def set_initMessage(colors,duration):
    """ modify init message that's sent to new websockets """
    global initMessage
    initMessage['colors'] = colors
    initMessage['duration'] = duration


def sendEvent(event):
    with lock:
        OverlayMessages.append(event) 


def set_PLAYER_NAMES(names):
    global PLAYER_NAMES
    PLAYER_NAMES.extend(names)


def initialize_AllReplays(ACCOUNTDIR):
    """ Creates a sorted dictionary of all replays with their times """
    AllReplays = set()
    for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                if file.endswith('.SC2Replay'):
                    file_path = os.path.join(root,file)
                    AllReplays.add(file_path)

    AllReplays = ((rep,os.path.getmtime(rep)) for rep in AllReplays)
    AllReplays = {k:{'created':v} for k,v in sorted(AllReplays,key=lambda x:x[1])}

    # Append already parsed replays
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

    return AllReplays


def check_replays(ACCOUNTDIR,AOM_NAME,AOM_SECRETKEY):
    """ Checks every few seconds for new replays  """
    global AllReplays
    global ReplayPosition
    session_games = {'Victory':0,'Defeat':0}

    with lock:
        AllReplays = initialize_AllReplays(ACCOUNTDIR)
        logger.info(f'Initializing AllReplays with length: {len(AllReplays)}')
        ReplayPosition = len(AllReplays) - 1

    while True:   
        current_time = time.time()
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                file_path = os.path.join(root,file)
                if file.endswith('.SC2Replay') and not(file_path in AllReplays): 
                    with lock:
                        AllReplays[file_path] = {'created':os.path.getmtime(file_path)}

                    if current_time - os.path.getmtime(file_path) < 60: 
                        logger.info(f'New replay: {file_path}')
                        replay_dict = dict()
                        try:   
                            replay_dict = analyse_replay(file_path,PLAYER_NAMES)

                            #good output
                            if len(replay_dict) > 1:
                                logger.debug('Replay analysis result looks good, appending...')
                                session_games[replay_dict['result']] += 1                                    
                                    
                                sendEvent({**replay_dict,**session_games})
                                with open(analysis_log_file, 'ab') as file: #save into a text file
                                    file.write((str(replay_dict)+'\n').encode('utf-8'))     

                            #no output                         
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
    """ function handling uploading the replay on the Aommaster's server"""

    if AOM_NAME == None or AOM_SECRETKEY == None:
        return

    if (time.time() - os.path.getmtime(file_path)) > 60:
        return

    if replay_dict.get('mainCommander',None) in [None,'']:
        sendEvent({'uploadEvent':True,'response':'Not valid replay for upload'})
        return

    url = f'http://starcraft2coop.com/scripts/assistant/replay.php?username={AOM_NAME}&secretkey={AOM_SECRETKEY}'
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file})
        logger.info(f'Replay upload reponse: {response.text}')
     
        if 'Success' in response.text or 'Error' in response.text:
            sendEvent({'uploadEvent':True,'response':response.text})
    
    except:
        sendEvent({'uploadEvent':True,'response':'Error'})
        logger.error(f'Failed to upload replay\n{traceback.format_exc()}')


async def manager(websocket, path):
    """ manages websocket connection for each client """
    overlayMessagesSent = 0
    logger.info(f"STARTING WEBSOCKET: {websocket}")
    await websocket.send(json.dumps(initMessage))
    logger.info(f"Sending init message: {initMessage}")
    while True:
        try:
            if len(OverlayMessages) > overlayMessagesSent:
                message = json.dumps(OverlayMessages[overlayMessagesSent])
                logger.info(f'Sending message #{overlayMessagesSent} through {websocket}')
                overlayMessagesSent += 1
                await websocket.send(message)
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
        finally:
            await asyncio.sleep(0.1)


def server_thread(PORT):
    """ creates a websocket server """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_server = websockets.serve(manager, 'localhost', PORT)
        logger.info('Starting websocket server')
        loop.run_until_complete(start_server)
        loop.run_forever()
    except:
        logger.error(traceback.format_exc())


def keyboard_thread_HIDE(HIDE):
    """ thread waiting for hide hotkey """
    logger.info('Starting keyboard hide thread')
    while True:
        keyboard.wait(HIDE)
        logger.info('Hide event')
        sendEvent({'hideEvent': True})


def keyboard_thread_SHOW(SHOW):
    """ thread waiting for show hotkey """
    logger.info('Starting keyboard show thread')
    while True:
        keyboard.wait(SHOW)
        logger.info('Show event')
        sendEvent({'showEvent': True})


def move_in_AllReplays(delta):
    global ReplayPosition

    logger.info(f'Attempt to move to {ReplayPosition + delta}/{len(AllReplays)-1}')

    #check if valid
    newPosition = ReplayPosition + delta
    if newPosition < 0 or newPosition >= len(AllReplays):
        logger.info(f'We have gone too far. Staying at {ReplayPosition}')
        return

    with lock:
        ReplayPosition = newPosition

    #get replay_dict of given replay
    key = list(AllReplays.keys())[ReplayPosition]
    if 'replay_dict' in AllReplays[key]:
        if AllReplays[key]['replay_dict'] != None:
            sendEvent(AllReplays[key]['replay_dict'])
        else:
            logger.info(f'This replay couldnt be analysed {key}')
            move_in_AllReplays(delta)
    else:
        #replay_dict is missing, analyse replay
        try: 
            replay_dict = analyse_replay(key,PLAYER_NAMES)
            if len(replay_dict) > 1:
                sendEvent(replay_dict)
                with lock:
                    AllReplays[key]['replay_dict'] = replay_dict
                with open(analysis_log_file, 'ab') as file:
                    file.write((str(replay_dict)+'\n').encode('utf-8'))  
            else:
                #no output from analysis
                with lock:
                    AllReplays[key]['replay_dict'] = None
                move_in_AllReplays(delta)
        except:
            logger.error(f'Failed to analyse replay: {key}')
            with lock:
                AllReplays[key]['replay_dict'] = None
            move_in_AllReplays(delta)


def keyboard_thread_OLDER(OLDER):
    """ thread waiting for hotkey for showing older replay"""
    logger.info('Starting keyboard older thread')

    while True:
        keyboard.wait(OLDER)
        move_in_AllReplays(-1)
        

def keyboard_thread_NEWER(NEWER):
    """ thread waiting for hotkey for showing newer replay"""
    logger.info('Starting keyboard newer thread')
    while True:
        keyboard.wait(NEWER)
        move_in_AllReplays(1)
