import asyncio
import websockets
from SnapshotManager import clientlog_filename
import time
import zipfile
import os
from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, imwrite
import cv2

# Task to handle the client connection
client_task = None
websocket = None  # Declare this to store the active websocket connection
# Initializing variables
global Ccamera_on # If server requests to toggle camera, this will be toggled
Ccamera_on = False # client_app.py checks if this variable changes every 1s
global livefeed_on # If server requests to start live feed, this will be toggled
livefeed_on = False 


async def close_connection(websocket):
    global client_task
    if client_task:
        client_task.cancel()  # Cancel the task to stop receiving messages
        try:
            await websocket.close()
            with open(clientlog_filename, 'w') as file:
                file.write(f"Connection closed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        except Exception as e:
            with open(clientlog_filename, 'w') as file:
                file.write(f"Error while closing connection: {e} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")

async def send_message(message, websocket):
    """Send a message to the server."""
    try:
        await websocket.send(message)
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def send_file(file_path, websocket, video=False):
    if video==False:
        try:
            file_name = file_path.split("/")[-1]
            await websocket.send(f"FILE:{file_name}")

            with open(file_path, "rb") as file:
                while chunk := file.read(1024):
                    await websocket.send(chunk)

            await websocket.send("EOF")
            print("File sent successfully")

        except Exception as e:
            print(f"Error: {e}")
    else:
        try:
            #file_name = file_path.split("/")[-1]
            await websocket.send(f"VIDEOFEED")

            #with open(file_path, "rb") as file:
            while chunk := file_path.read(1024):
                await websocket.send(chunk)

            await websocket.send("EOF")
            print("File sent successfully")

        except Exception as e:
            print(f"Error: {e}")

async def live_feed(websocket):
    global livefeed_on
    # Initialize the camera
    cap = VideoCapture(0)
    if not cap.isOpened():
        with open(clientlog_filename, 'w') as file:
            file.write(f"Error: Could not open camera for live feed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        return

    while livefeed_on:
        ret, frame = cap.read()
        if not ret:
            with open(clientlog_filename, 'w') as file:
                file.write(f"Error: Could not read frame taken for live feed at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            break

        # Send the frame to the server
        #frame_path = f"cache/livefeed_{int(time.time())}.jpg"
        #imwrite(frame_path, frame)
        await send_file(frame, websocket, video=True)
        time.sleep(0.143)

    await send_message("FEED_OVER", websocket)

    # Release the camera and close the window
    cap.release()
    destroyAllWindows()

async def receive_messages(websocket):
    global Ccamera_on
    global client_task
    global livefeed_on
    try:
        while True:
            message = await websocket.recv()
            if message.startswith("FILE:"):
                print(f"Server: {message[5:]}")
            elif message == "STARTCAMERA":
                Ccamera_on = True
                print(f"Server started camera {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Camera started by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            elif message == "SHUTDOWN":
                Ccamera_on = False
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Camera paused by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            elif message == "DISCONNECT":
                await close_connection(websocket)
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Connection closed by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                break
            elif message == "DOWNLOADALL":
                # Paths to files and folder to be zipped
                files_to_zip = ['face_timestamps.pkl', 'face_encodings.pkl', clientlog_filename]
                snapshots_folder = 'snapshots'  # Folder containing snapshots
                zip_filename = f"client_data_{int(time.time())}.zip"
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Server requested to download all data at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                # Create a zip file
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for file in files_to_zip:
                        if os.path.exists(file):
                            zipf.write(file)
                    # Add the entire 'snapshots' folder if it exists
                    if os.path.exists(snapshots_folder):
                        for foldername, subfolders, filenames in os.walk(snapshots_folder):
                            for filename in filenames:
                                file_path = os.path.join(foldername, filename)
                                zipf.write(file_path)

                # Send the zip file to the server
                await send_file(zip_filename, websocket)

                # Remove the zip file after sending
                os.remove(zip_filename)
                with open(clientlog_filename, 'w') as file:
                    file.write(f"{zip_filename} sent to server at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")

            elif message == "DOWNLOADLOG":
                # Send most recent log.txt
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Server requested to download latest log {clientlog_filename} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                await send_file(clientlog_filename, websocket)

            elif message == "DOWNLOADFACES":
                # Create a zip file
                zip_filename = f"detected_faces_{int(time.time())}.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    # Add the entire 'snapshots' folder if it exists
                    if os.path.exists('snapshots'):
                        for foldername, subfolders, filenames in os.walk(snapshots_folder):
                            for filename in filenames:
                                file_path = os.path.join(foldername, filename)
                                zipf.write(file_path)

                # Send the zip file to the server
                await send_file(zip_filename, websocket)

                # Remove the zip file after sending
                os.remove(zip_filename)
                with open(clientlog_filename, 'w') as file:
                    file.write(f"{zip_filename} sent to server at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                
            elif message == "LIVEFEED":
                # Begin taking snapshots and sending them to the server
                livefeed_on = not livefeed_on
                if livefeed_on:
                    await live_feed(websocket)
                pass
            else:
                print(f"Message from server: {message}")

    except websockets.ConnectionClosedOK:
        print("Server closed the connection")
    except websockets.ConnectionClosedError as e:
        print(f"Connection was closed with an error: {e}")
    except Exception as e:
        print(f"Error: {e}")

async def start_client():
    global client_task, websocket
    uri = "ws://localhost:8765"
    try:
        websocket = await websockets.connect(uri)
        with open(clientlog_filename, 'w') as file:
            file.write(f"Connected to the server at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        client_task = asyncio.create_task(receive_messages(websocket))
        await client_task
    except Exception as e:
        with open(clientlog_filename, 'w') as file:
            file.write(f"Error connecting to the server: {e} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")