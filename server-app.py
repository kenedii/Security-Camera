import customtkinter as ctk
import asyncio
import server
import threading
import tkinter as tk  # Required for IntVar
from PIL import Image, ImageTk
import io

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Initialize the Tkinter root
root = ctk.CTk()
root.title("123SecurityCam - Server App")
root.geometry("800x600")

# Now declare selected_client after root is created
selected_client = tk.IntVar()

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def update_client_status():
    previous_clients = []
    while True:
        clients = server.list_all_clients()
        selected = selected_client.get()

        # Only refresh if the client list has changed (i.e., new client or disconnection)
        if clients != previous_clients:
            list_clients(clients)
            previous_clients = clients  # Update previous_clients to the latest state

        # Update the action buttons if a client is selected
        if selected:
            camera_on = next((camera_on for cid, camera_on in clients if cid == selected), False)
            update_action_buttons(camera_on)
        
        await asyncio.sleep(2)  # Check every 2 seconds

def on_start_server():
    global server_instance
    # Schedule the coroutine to be executed
    future = asyncio.run_coroutine_threadsafe(server.start_server(), loop)
    server_instance = future.result()  # Store the server instance
    
    # Hide the start button and show the close button
    b_startserver.pack_forget()
    b_closeserver.pack(pady=12, padx=10)
    
    # Show the client and actions frames and list clients
    client_frame.pack(side="left", fill="y", padx=20, pady=20)
    actions_frame.pack(side="left", fill="y", padx=20, pady=20)
    
    # Start the client status checker
    asyncio.run_coroutine_threadsafe(update_client_status(), loop)

def on_close_server():
    # Schedule the coroutine to close the server
    asyncio.run_coroutine_threadsafe(server.close_server(server_instance), loop)

    # Hide the close button and show the start button
    b_closeserver.pack_forget()
    b_startserver.pack(pady=12, padx=10)
    
    # Hide the client and actions frames
    client_frame.pack_forget()
    actions_frame.pack_forget()

def send_action_to_selected_client(action):
    client_id = selected_client.get()  # Get the selected client from the IntVar
    if client_id == 0:  # No client is selected
        print("No client selected")
        return
    
    # Send the action to the selected client
    message = f"{action}"
    asyncio.run_coroutine_threadsafe(server.send_message_to_specific_client(client_id, message), loop)
    print(f"Sent '{action}' to Client {client_id}")

def update_action_buttons(camera_on):
    """ Update the state of action buttons based on camera status """
    state = 'normal' if camera_on else 'disabled'
    b_livefeed.configure(state=state)
    b_viewfaces.configure(state=state)
    b_downlog.configure(state=state)
    b_downdata.configure(state=state)
    
    if camera_on:
        b_shutdowncam.configure(text="Shutdown Camera", command=lambda: send_action_to_selected_client("SHUTDOWN"))
    else:
        b_shutdowncam.configure(text="Start Camera", command=lambda: send_action_to_selected_client("STARTCAMERA"))

def on_client_selection(*args):
    client_id = selected_client.get()
    if client_id != 0:
        # Check if the selected client's camera is on or off
        clients = server.list_all_clients()
        camera_on = next((camera_on for cid, camera_on in clients if cid == client_id), False)
        update_action_buttons(camera_on)
        b_shutdowncam.configure(state='normal')  # Enable the button
    else:
        # No client selected, disable all buttons and set default button text
        b_shutdowncam.configure(text="Start Camera", command=lambda: send_action_to_selected_client("STARTCAMERA"))
        b_shutdowncam.configure(state='disabled')  # Disable the button
        update_action_buttons(False)

def on_start_feed():
    # Schedule the coroutine to be executed
    asyncio.run_coroutine_threadsafe(toggle_live_feed_window(), loop)

async def toggle_live_feed_window():
    """Toggles the live feed window for the selected client."""
    client_id = selected_client.get()
    if client_id == 0:
        print("No client selected")
        return

    # Request the live feed from the client
    await server.send_message_to_specific_client(client_id, "LIVEFEED")

    # Create the live feed window
    feed_window = ctk.CTkToplevel(root)
    feed_window.title(f"Live Feed - Client {client_id}")
    feed_window.geometry("800x600")

    # Label to display the video feed
    video_label = ctk.CTkLabel(master=feed_window)
    video_label.pack(fill="both", expand=True)

    def update_video_feed():
        nonlocal client_id
        video_frame = server.lf_video_frame.get(client_id)

        if video_frame:
            try:
                # Decode the byte stream into an image
                image = Image.open(io.BytesIO(video_frame))
                image_tk = ImageTk.PhotoImage(image)
                video_label.configure(image=image_tk)
                video_label.image = image_tk
            except Exception as e:
                print(f"Error updating video feed: {e}")

        # Schedule the next frame update
        feed_window.after(50, update_video_feed)

    def on_window_close():
        # Send a message to stop the live feed
        asyncio.run_coroutine_threadsafe(
            server.send_message_to_specific_client(client_id, "LIVEFEED"),
            loop
        )
        feed_window.destroy()

    # Handle window close event
    feed_window.protocol("WM_DELETE_WINDOW", on_window_close)

    # Start updating the video feed
    update_video_feed()


def list_clients(clients=None):
    global selected_client  # Ensure we are using the global selected_client variable
    
    # Clear the client list frame
    for widget in client_frame.winfo_children():
        widget.destroy()

    # Add the label for connected clients
    label_clients = ctk.CTkLabel(master=client_frame, text="Connected clients", font=("Arial", 18))
    label_clients.grid(row=0, column=0, columnspan=2, pady=10)

    # Get the list of clients from the server if not passed
    clients = clients if clients else server.list_all_clients()

    # Reset selected_client variable to ensure a new selection can be made
    selected_client.set(0)

    # List all clients with checkboxes and status indicators
    for idx, (client_id, camera_on) in enumerate(clients, start=1):  # Start client ID from 1
        status_color = "green" if camera_on else "red"
        status_circle = ctk.CTkLabel(master=client_frame, text="●", text_color=status_color, font=("Arial", 18))
        status_circle.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
        
        checkbox = ctk.CTkRadioButton(master=client_frame, text=f"Client {client_id}", variable=selected_client, value=client_id)
        checkbox.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

# Create an event loop for the background thread
loop = asyncio.new_event_loop()
threading.Thread(target=start_event_loop, args=(loop,), daemon=True).start()

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="123SecurityCam - Server App", font=("Arial", 24)) # Title
label.pack(pady=12, padx=10)

b_startserver = ctk.CTkButton(master=frame, text="Start Server", command=on_start_server) # Start server button
b_startserver.pack(pady=12, padx=10)

b_closeserver = ctk.CTkButton(master=frame, text="Close Server", command=on_close_server) # Close server button

# Create a frame for the list of clients (initially hidden)
client_frame = ctk.CTkFrame(master=root, width=200)

# Create a frame for the actions section (initially hidden)
actions_frame = ctk.CTkFrame(master=root, width=200)

# Add a label for the "Actions" section
label_actions = ctk.CTkLabel(master=actions_frame, text="Actions", font=("Arial", 18))
label_actions.pack(pady=10)

# Modify the action buttons to send specific actions to the selected client
b_livefeed = ctk.CTkButton(master=actions_frame, text="View Live Feed", command=on_start_feed)
b_livefeed.pack(pady=5)

b_viewfaces = ctk.CTkButton(master=actions_frame, text="Download Faces", command=lambda: send_action_to_selected_client("DOWNLOADFACES"))
b_viewfaces.pack(pady=5)

b_downlog = ctk.CTkButton(master=actions_frame, text="Download Log", command=lambda: send_action_to_selected_client("DOWNLOADLOG"))
b_downlog.pack(pady=5)

b_downdata = ctk.CTkButton(master=actions_frame, text="Download all Data", command=lambda: send_action_to_selected_client("DOWNLOADALL"))
b_downdata.pack(pady=5)

b_shutdowncam = ctk.CTkButton(master=actions_frame, text="Start Camera", command=lambda: send_action_to_selected_client("STARTCAMERA"))
b_shutdowncam.pack(pady=5)

# Bind the selected_client variable to the on_client_selection function
selected_client.trace_add("write", on_client_selection)

# Initialize the state of action buttons when the app starts
update_action_buttons(False)  # Initially, no client selected, so buttons should be disabled

# Run the Tkinter main loop
root.mainloop()
