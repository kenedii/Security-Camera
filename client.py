import asyncio
import websockets
import client_app

# Task to handle the client connection
client_task = None
websocket = None  # Declare this to store the active websocket connection

async def close_connection(websocket):
    global client_task
    if client_task:
        client_task.cancel()  # Cancel the task to stop receiving messages
        try:
            await websocket.close()
            print("Connection closed successfully")
        except Exception as e:
            print(f"Error while closing connection: {e}")

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
            elif message == "PAUSECAM":
                client_app.toggle_camera()
            elif message == "SHUTDOWN":
                await close_connection(websocket)
                print("Server requested to close the connection")
                break
            elif message == "DOWNLOADALL":
                # Send face_timestamps.pkl, face_encodings.pkl, log.txt, DetectionLog.txt, and 'snapshots' folder
                pass
            elif message == "DOWNLOADLOG":
                # Send most recent log.txt and DetectionLog.txt
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
        print("Connected to the server")
        client_task = asyncio.create_task(receive_messages(websocket))
        await client_task
    except Exception as e:
        print(f"Error connecting to the server: {e}")
