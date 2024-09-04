import asyncio
import websockets

async def send_file(file_path, websocket):
    try:
        # Send the file name first, prefixed with "FILE:" to indicate it's a file transfer
        file_name = file_path.split("/")[-1]
        await websocket.send(f"FILE:{file_name}")

        # Send the file content
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):
                await websocket.send(chunk)

        # Send EOF to indicate the end of the file
        await websocket.send("EOF")
        print("File sent successfully")

    except Exception as e:
        print(f"Error: {e}")

async def receive_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            
            # Check if the message is a file-related message
            if message.startswith("FILE:"):
                print(f"Server: {message[5:]}")
            else:
                # General message from the server
                print(f"Message from server: {message}")

    except websockets.ConnectionClosedOK:
        print("Server closed the connection")
    except Exception as e:
        print(f"Error: {e}")

async def main(file_path):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Start receiving messages in the background
        receive_task = asyncio.create_task(receive_messages(websocket))

        # Send the file to the server
        await send_file(file_path, websocket)

        # Wait for the receive task to complete
        await receive_task

if __name__ == "__main__":
    file_path = "path/to/your/file.txt"  # Replace with your file path
    asyncio.run(main(file_path))
