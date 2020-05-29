import os
import sys
import json
import time
import keyboard
import traceback
import asyncio
import websockets

from ReplayAnalysis import analyse_replay

### Storage for all messages
OverlayMessages = []

def check_replays(ACCOUNTDIR,PLAYER_NAMES):
    """ Checks every 4s for new replays  """
    global OverlayMessages

    already_checked_replays = set()
    while True:   
        current_time = time.time()
        for root, directories, files in os.walk(ACCOUNTDIR):
            for file in files:
                file_path = os.path.join(root,file)
                if file.endswith('.SC2Replay') and not(file_path in already_checked_replays):
                    already_checked_replays.add(file_path)

                    if current_time - os.path.getmtime(file_path) < 60: 
                        try:   
                            replay_message, replay_dict = analyse_replay(file_path,PLAYER_NAMES)
                            if replay_message != '':                           
                                if len(replay_dict) > 0 :
                                    OverlayMessages.append(replay_dict) #save in queue to send

                                    with open('ReplayAnalysisLog.txt', 'ab') as file: #save into a text file
                                        file.write(('\n\n'+str(replay_dict)).encode('utf-8'))
                            else:
                                print(f'ERROR: No output from replay analysis ({file})') 
                            break
                        except Exception as e:
                            exc_type, exc_value, exc_tb = sys.exc_info()
                            traceback.print_exception(exc_type, exc_value, exc_tb)

        time.sleep(4)   


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


def server_thread(PORT):
    """ creates a websocket server """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        start_server = websockets.serve(manager, 'localhost', PORT)
        print('Starting websocket server')
        loop.run_until_complete(start_server)
        loop.run_forever()
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)


def keyboard_thread_HIDE(HIDE):
    print('Starting keyboard HIDE thread')
    while True:
        keyboard.wait(HIDE)
        OverlayMessages.append({'hideEvent': True})


def keyboard_thread_SHOW(SHOW):
    print('Starting keyboard SHOW thread')
    while True:
        keyboard.wait(SHOW)
        OverlayMessages.append({'showEvent': True})