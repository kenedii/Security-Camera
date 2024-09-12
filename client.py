import asyncio
import websockets
import client_app
from SnapshotManager import clientlog_filename
import time
import zipfile
import os
import shutil

# Task to handle the client connection
client_task = None
websocket = None  # Declare this to store the active websocket connection

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
            file_name = file_path.split("/")[-1]
            await websocket.send(f"VIDEOFEED")

            with open(file_path, "rb") as file:
                while chunk := file.read(1024):
                    await websocket.send(chunk)

            await websocket.send("EOF")
            print("File sent successfully")

        except Exception as e:
            print(f"Error: {e}")

async def receive_messages(websocket):
    global client_task
    try:
        while True:
            message = await websocket.recv()
            if message.startswith("FILE:"):
                print(f"Server: {message[5:]}")
            elif message == "STARTCAM":
                client_app.toggle_camera()
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Camera started by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            elif message == "PAUSECAM":
                client_app.toggle_camera()
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Camera paused by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            elif message == "SHUTDOWN":
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
