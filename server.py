# Flask websocket server to control the cameras.
# Requests camera feed from clients or receives pkl data, snapshots, and live camera feed from clients.
import asyncio
import websockets

async def handle_client(websocket, path):
    try:
        print("Client connected")

        # Receive file name
        file_name = await websocket.recv()
        print(f"Receiving file: {file_name}")

        # Receive file content
        with open(file_name, "wb") as file:
            while True:
                data = await websocket.recv()
                if data == "EOF":
                    print("File received successfully")
                    break
                file.write(data)

    except websockets.ConnectionClosedOK:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
