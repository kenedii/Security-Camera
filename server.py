import asyncio
import websockets
import os

global lf_video_frame
lf_video_frame = None
global lf_on
lf_on = False

clients = {}  # Dictionary to track connected clients with their unique identifier

async def handle_client(websocket, path):
    global lf_video_frame
    global lf_on

    # Assign a unique identifier for each client
    client_id = len(clients) + 1
    clients[client_id] = {'websocket': websocket, 'camera_on': False}
    print(f"Client {client_id} connected")

    # Create a directory for this client if it doesn't already exist
    client_folder = f"client_data/{client_id}"
    os.makedirs(client_folder, exist_ok=True)

    try:
        while True:
            # Receive the first message and check if it's a file or a regular message
            message = await websocket.recv()

            if message.startswith("FILE:"):
                # Handle file transfer
                file_name = message[5:]
                file_path = os.path.join(client_folder, file_name)
                print(f"Receiving file from Client {client_id}: {file_name}")

                with open(file_path, "wb") as file:
                    while True:
                        data = await websocket.recv()
                        if data == "EOF":
                            print(f"File received successfully from Client {client_id}")
                            break
                        file.write(data)

                # Confirm file received
                await websocket.send(f"File {file_name} received successfully and saved to {file_path}")

            if message == ("VIDEOFEED"):
                # Handle file transfer
                #print(f"Receiving video feed data from Client {client_id}")
                
                while True:
                    data = await websocket.recv()
                    lf_video_frame = data
                    if data == "EOF":
                        print(f"vf image received successfully from Client {client_id}")
                        break

                # Confirm file received
                #await websocket.send(f"File {file_name} received successfully and saved to {file_path}")

            elif message.startswith("FEED_"):
                if message == "FEED_ON":
                    lf_on = True
                    #print(f"Client {client_id} started the live feed")
                elif message == "FEED_OVER":
                    lf_on = False
                    #print(f"Client {client_id} stopped the live feed")

            elif message == "CAMERAON":
                clients[client_id]['camera_on'] = True
                print(f"Client {client_id} turned the camera ON")

            elif message == "CAMERAOFF":
                clients[client_id]['camera_on'] = False
                print(f"Client {client_id} turned the camera OFF")

            else:
                # Treat it as a regular message
                print(f"Received from Client {client_id}: {message}")
                await websocket.send(f"Server received: {message}")

    except websockets.ConnectionClosedOK:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Error with Client {client_id}: {e}")
    finally:
        del clients[client_id]

async def send_message_to_all_clients(message):
    if clients:
        await asyncio.wait([client['websocket'].send(message) for client in clients.values()])
        print(f"Sent to all clients: {message}")
    else:
        print("No clients connected")

async def send_message_to_specific_client(client_id, message):
    if client_id in clients:
        await clients[client_id]['websocket'].send(message)
        print(f"Sent to Client {client_id}: {message}")
    else:
        print(f"Client {client_id} not connected")

def list_all_clients():
    return [(client_id, client_data['camera_on']) for client_id, client_data in clients.items()]

async def close_server(server):
    server.close()
    await server.wait_closed()
    print("Server has been closed")

async def start_server():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Server started on ws://localhost:8765")

    # Allow sending messages to clients from the server console
    """
    try:
        while True:
            command = input("Enter 'all' to send to all clients, 'send' to send to a specific client, 'list' to list all clients, 'close' to shut down the server: ").strip()
            
            if command == "all":
                message = input("Enter message to send to all clients: ")
                await send_message_to_all_clients(message)
            
            elif command == "send":
                client_id = int(input("Enter client ID to send message to: "))
                message = input(f"Enter message to send to Client {client_id}: ")
                await send_message_to_specific_client(client_id, message)
            
            elif command == "list":
                clients_list = list_all_clients()
                print(f"Connected clients: {clients_list}")

            elif command == "close":
                await close_server(server)
                break  # Exit the loop after closing the server

    except KeyboardInterrupt:
        print("Server interrupted by user")
        await close_server(server)
    """

    return server
