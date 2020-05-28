import os
import sys
import json
import time
import traceback
import threading
import websockets
import asyncio
import configparser

import LocalOverlay
from ReplayAnalysis import analyse_replay

### Config setup
config = configparser.ConfigParser()
config.read('OverlayConfig.ini')

ACCOUNTDIR = os.path.join(os.path.expanduser('~'),'Documents\\StarCraft II\\Accounts')
if 'ACCOUNTDIR' in config['CONFIG']:
    ACCOUNTDIR = config['CONFIG']['ACCOUNTDIR']

SHOWOVERLAY = True
if 'SHOWOVERLAY' in config['CONFIG']:
    SHOWOVERLAY = config['CONFIG']['SHOWOVERLAY']
    if SHOWOVERLAY.lower() in ['false','0','no']:
        SHOWOVERLAY = False

PLAYER_NAMES = []
if 'PLAYER_NAMES' in config['CONFIG']:
    for player in config['CONFIG']['PLAYER_NAMES'].split(','):
        PLAYER_NAMES.append(player)

### Storage for all messages
OverlayMessages = []


def check_replays():
    """ Checks every 2s for new replays  """
    global OverlayMessages

    already_opened_replays = []
    while True:   
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                if file.endswith('.SC2Replay') and not(file in already_opened_replays):
                    file_path = os.path.join(root,file)
                    try:
                        if (time.time() - os.stat(file_path).st_mtime < 60):                            
                            replay_message, replay_dict = analyse_replay(file_path,PLAYER_NAMES)
                            if replay_message != '':
                                already_opened_replays.append(file)
                                if len(replay_dict) > 0 :

                                    print(f'Appending: {replay_dict}')
                                    OverlayMessages.append(replay_dict) #save in queue to send

                                    with open('ReplayAnalysisLog.txt', 'ab') as file: #save into a text file
                                        file.write(('\n\n'+str(replay_dict)).encode('utf-8'))
                            else:
                                print(f'ERROR: No output from replay analysis ({file})') 
                            break
                    except Exception as e:
                        exc_type, exc_value, exc_tb = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_tb)

        time.sleep(2)   



async def manager(websocket, path):
    """ manages websocket connection for each client """
    overlayMessagesSent = 0
    print(f"---STARTING WEBSOCKET: {websocket}")
    while True:
        try:
            if len(OverlayMessages) > overlayMessagesSent:
                message = json.dumps(OverlayMessages[overlayMessagesSent])
                print(f'Sending message #{overlayMessagesSent} through {websocket}')
                overlayMessagesSent += 1
                await websocket.send(message)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
        finally:
            await asyncio.sleep(1)



def server_thread():
    """ creates a websocket server """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_server = websockets.serve(manager, 'localhost', LocalOverlay.PORT)
        print('Starting websocket server')
        loop.run_until_complete(start_server)
        loop.run_forever()
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)



def main():
    t1 = threading.Thread(target = LocalOverlay.main, args=(SHOWOVERLAY,))
    t1.start()
    t2 = threading.Thread(target = check_replays, daemon=True)
    t2.start()
    t3 = threading.Thread(target = server_thread, daemon=True)
    t3.start()

    # When the overlay thread is closed (via tray quit), quit the app (and kill daemon threads)
    t1.join()
    sys.exit()


if __name__ == "__main__":
    main()