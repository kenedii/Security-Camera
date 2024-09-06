import asyncio
import websockets

# Flag to control when to stop receiving messages
should_run = True

async def close_connection(websocket):
    global should_run
    try:
        should_run = False  # Stop receiving messages
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
    global should_run
    try:
        while should_run:  # Only continue while the flag is True
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
    async with websockets.connect(uri) as websocket:
        try:
            print("Connected to the server")
            receive_task = asyncio.create_task(receive_messages(websocket))

            # Wait for the receive task to complete (this will run until the connection is closed)
            await receive_task
        except Exception as e:
            print(f"Connection error: {e}")
