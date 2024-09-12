import asyncio
import websockets
import client_app
from SnapshotManager import clientlog_filename
import time

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
                file.close()
        except Exception as e:
            with open(clientlog_filename, 'w') as file:
                file.write(f"Error while closing connection: {e} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                file.close()

async def send_message(message, websocket):
    """Send a message to the server."""
    try:
        await websocket.send(message)
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def send_file(file_path, websocket):
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
                    file.close()
            elif message == "PAUSECAM":
                client_app.toggle_camera()
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Camera paused by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                    file.close()
            elif message == "SHUTDOWN":
                await close_connection(websocket)
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Connection closed by server request at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                    file.close()
                break
            elif message == "DOWNLOADALL":
                # Send face_timestamps.pkl, face_encodings.pkl, log.txt, and 'snapshots' folder
                pass
            elif message == "DOWNLOADLOG":
                # Send most recent log.txt
                with open(clientlog_filename, 'w') as file:
                    file.write(f"Server requested to download latest log {clientlog_filename} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                    file.close()
                await send_file(clientlog_filename, websocket)

                pass
            elif message == "VIEWFACES":
                # Go through the 'snapshots' folder and send the image of each face
                pass
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
            file.close()
        client_task = asyncio.create_task(receive_messages(websocket))
        await client_task
    except Exception as e:
        with open(clientlog_filename, 'w') as file:
            file.write(f"Error connecting to the server: {e} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            file.close()
