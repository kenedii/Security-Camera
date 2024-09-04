import asyncio
import websockets

async def send_file(file_path, websocket):
    try:
        # Send the file name first
        file_name = file_path.split("/")[-1]
        await websocket.send("FILE:"+file_name)

        # Send the file content
        with open(file_path, "rb") as file:
            while chunk := file.read(1024):
                await websocket.send(chunk)

        # Send EOF to indicate the end of the file
        await websocket.send("EOF")
        print("File sent successfully")

    except Exception as e:
        print(f"Error: {e}")

async def main(file_path):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await send_file(file_path, websocket)

if __name__ == "__main__":
    file_path = "path/to/your/file.txt"  # Replace with your file path
    asyncio.run(main(file_path))
