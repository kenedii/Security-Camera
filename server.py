import asyncio
import websockets

clients = {}  # Dictionary to track connected clients with their unique identifier

async def handle_client(websocket, path):
    # Assign a unique identifier for each client
    client_id = len(clients) + 1
    clients[client_id] = websocket
    print(f"Client {client_id} connected")

    try:
        # Receive file name
        file_name = await websocket.recv()
        print(f"Receiving file from Client {client_id}: {file_name}")

        # Receive file content
        with open(file_name, "wb") as file:
            while True:
                data = await websocket.recv()
                if data == "EOF":
                    print(f"File received successfully from Client {client_id}")
                    break
                file.write(data)

        # After receiving the file, send a confirmation message to the client
        await websocket.send(f"File {file_name} received successfully")

        # Keep the connection open for further communication
        while True:
            message = await websocket.recv()
            if message == "exit":
                print(f"Client {client_id} requested to close the connection")
                break
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
        await asyncio.wait([client.send(message) for client in clients.values()])
        print(f"Sent to all clients: {message}")
    else:
        print("No clients connected")

async def send_message_to_specific_client(client_id, message):
    if client_id in clients:
        await clients[client_id].send(message)
        print(f"Sent to Client {client_id}: {message}")
    else:
        print(f"Client {client_id} not connected")

def list_all_clients():
    return list(clients.keys())

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Server started on ws://localhost:8765")

    # Allow sending messages to clients from the server console
    while True:
        command = input("Enter 'all' to send to all clients, 'send' to send to a specific client, 'list' to list all clients: ").strip()
        
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

if __name__ == "__main__":
    asyncio.run(main())
