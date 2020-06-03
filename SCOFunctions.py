import os
import sys
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

def get_OverlayMessages():
    return OverlayMessages

def get_lock():
    return lock

def check_replays(ACCOUNTDIR,PLAYER_NAMES,REPLAYTIME,AOM_NAME,AOM_SECRETKEY):
    """ Checks every 4s for new replays  """
    already_checked_replays = set()
    while True:   
        current_time = time.time()
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                file_path = os.path.join(root,file)
                if file.endswith('.SC2Replay') and not(file_path in already_checked_replays):
                    
                    already_checked_replays.add(file_path)

                    if current_time - os.path.getmtime(file_path) < REPLAYTIME: 
                        logger.debug(f'New replay: {file_path}')
                        try:   
                            replay_dict = analyse_replay(file_path,PLAYER_NAMES)
                            if len(replay_dict) > 0 :
                                logger.debug('Replay analysis result looks good, appending...')
                                lock.acquire()
                                OverlayMessages.append(replay_dict) #save in queue to send
                                lock.release()
                                if not(replay_dict['mainCommander'] in [None,'']):
                                    upload_to_aom(file_path,AOM_NAME,AOM_SECRETKEY)    
                                with open('SCO_analysis_log.txt', 'ab') as file: #save into a text file
                                    file.write((str(replay_dict)+'\n').encode('utf-8'))                              
                            else:
                                logger.error(f'ERROR: No output from replay analysis ({file})') 
                            break
                        except Exception as e:
                            exc_type, exc_value, exc_tb = sys.exc_info()
                            logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')

        time.sleep(3)   


def upload_to_aom(file_path,AOM_NAME,AOM_SECRETKEY):
    """ function handling uploading the replay on the Aommaster's server"""
    if AOM_NAME == None or AOM_SECRETKEY==None:
        return

    url = f'http://starcraft2coop.com/scripts/assistant/replay.php?username={AOM_NAME}&secretkey={AOM_SECRETKEY}'
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file})
        logger.info(f'Replay upload reponse: {response.text}')
     
        if 'Success' in response.text or 'Error' in response.text:
            lock.acquire()
            OverlayMessages.append({'uploadEvent':True,'response':response.text})
            lock.release()
    
    except Exception as e:
        lock.acquire()
        OverlayMessages.append({'uploadEvent':True,'response':'Error'})
        lock.release()
        exc_type, exc_value, exc_tb = sys.exc_info()
        logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')


async def manager(websocket, path):
    """ manages websocket connection for each client """
    overlayMessagesSent = 0
    logger.info(f"STARTING WEBSOCKET: {websocket}")
    while True:
        try:
            if len(OverlayMessages) > overlayMessagesSent:
                message = json.dumps(OverlayMessages[overlayMessagesSent])
                logger.info(f'Sending message #{overlayMessagesSent} through {websocket}')
                overlayMessagesSent += 1
                await websocket.send(message)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')
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
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')


def keyboard_thread_HIDE(HIDE):
    logger.info('Starting keyboard hide thread')
    while True:
        keyboard.wait(HIDE)
        logger.info('Hide event')
        lock.acquire()
        OverlayMessages.append({'hideEvent': True})
        lock.release()


def keyboard_thread_SHOW(SHOW):
    logger.info('Starting keyboard show thread')
    while True:
        keyboard.wait(SHOW)
        logger.info('Show event')
        lock.acquire()
        OverlayMessages.append({'showEvent': True})
        lock.release()