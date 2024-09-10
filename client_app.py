import customtkinter as ctk
import asyncio
import client
import threading
import SnapshotManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Initialize the Tkinter root
root = ctk.CTk()
root.title("123SecurityCam - Client App")
root.geometry("800x600")

# Create an event loop for the background thread
loop = asyncio.new_event_loop()
threading.Thread(target=lambda: asyncio.set_event_loop(loop) or loop.run_forever(), daemon=True).start()

# Track camera state (initially off)
camera_on = False

# Function to update the button and send message to the server
def toggle_camera():
    global camera_on
    if client.websocket:  # Ensure websocket connection exists
        camera_on = not camera_on

        # Update the button text and indicator color
        if camera_on:
            b_toggle_camera.configure(text="Stop Camera")
            l_indicator.configure(text="●", text_color="green")
            # Send CAMERAON message to the server
            asyncio.run_coroutine_threadsafe(client.send_message("CAMERAON", client.websocket), loop)
        else:
            b_toggle_camera.configure(text="Start Camera")
            l_indicator.configure(text="●", text_color="red")
            # Send CAMERAOFF message to the server
            asyncio.run_coroutine_threadsafe(client.send_message("CAMERAOFF", client.websocket), loop)
    else:
        print("Client not connected to the server.")

def on_start_client():
    # Schedule the coroutine to start the client
    asyncio.run_coroutine_threadsafe(client.start_client(), loop)

    # Enable the camera toggle button once the client is connected
    b_toggle_camera.configure(state="normal")

    # Hide the start button after the client is started
    b_startclient.pack_forget()
    b_closeclient.pack(pady=12, padx=10)

def on_close_client():
    global camera_on
    # Send CAMERAOFF message if the camera is on
    if camera_on and client.websocket:
        asyncio.run_coroutine_threadsafe(client.send_message("CAMERAOFF", client.websocket), loop)
    
    # Schedule the coroutine to close the client connection
    if client.client_task:
        asyncio.run_coroutine_threadsafe(client.close_connection(client.websocket), loop)

    # Disable the camera toggle button after the client is closed
    b_toggle_camera.configure(state="disabled")

    # Set camera state to off and update button and indicator
    camera_on = False
    b_toggle_camera.configure(text="Start Camera")
    l_indicator.configure(text="●", text_color="red")

    # Hide the close button after the client is closed
    b_closeclient.pack_forget()
    b_startclient.pack(pady=12, padx=10)

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="123SecurityCam - Client App", font=("Arial", 24))
label.pack(pady=12, padx=10)

b_startclient = ctk.CTkButton(master=frame, text="Start Client", command=on_start_client)
b_startclient.pack(pady=12, padx=10)

b_closeclient = ctk.CTkButton(master=frame, text="Close Client", command=on_close_client)

# Camera toggle button and indicator (initially disabled)
b_toggle_camera = ctk.CTkButton(master=frame, text="Start Camera", command=toggle_camera, state="disabled")
b_toggle_camera.pack(pady=12, padx=10)

l_indicator = ctk.CTkLabel(master=frame, text="●", font=("Arial", 24), text_color="red")
l_indicator.pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
