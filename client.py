import asyncio
import websockets

# Task to handle the client connection
client_task = None

async def close_connection(websocket):
    global client_task
    if client_task:
        client_task.cancel()  # Cancel the task to stop receiving messages
        try:
            await websocket.close()
            print("Connection closed successfully")
        except Exception as e:
            print(f"Error while closing connection: {e}")

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
            else:
                print(f"Message from server: {message}")

    except websockets.ConnectionClosedOK:
        print("Server closed the connection")
    except websockets.ConnectionClosedError as e:
        print(f"Connection was closed with an error: {e}")
    except Exception as e:
        print(f"Error: {e}")

async def start_client():
    uri = "ws://localhost:8765"
    global client_task
    async with websockets.connect(uri) as websocket:
        print("Connected to the server")
        client_task = asyncio.create_task(receive_messages(websocket))
        await client_task
