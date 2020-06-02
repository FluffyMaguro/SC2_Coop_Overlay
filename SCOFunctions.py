import os
import sys
import json
import time
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
logger = logclass('SCOF','DEBUG')

def get_OverlayMessages():
    return OverlayMessages

def get_lock():
    return lock

def check_replays(ACCOUNTDIR,PLAYER_NAMES,REPLAYTIME):
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
                                with open('SCO_analysis_log.txt', 'ab') as file: #save into a text file
                                    file.write((str(replay_dict)).encode('utf-8')+'\n')
                            else:
                                logger.error(f'ERROR: No output from replay analysis ({file})') 
                            break
                        except Exception as e:
                            exc_type, exc_value, exc_tb = sys.exc_info()
                            logger.error(f'{exc_type}\n{exc_value}\n{exc_tb}')

        time.sleep(3)   


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