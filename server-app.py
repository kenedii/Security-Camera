import customtkinter as ctk
import asyncio
import server
import threading
import tkinter as tk  # Required for IntVar

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
    list_clients()

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
    message = f"Action: {action}"
    asyncio.run_coroutine_threadsafe(server.send_message_to_specific_client(client_id, message), loop)
    print(f"Sent '{action}' to Client {client_id}")

def list_clients():
    global selected_client  # Ensure we are using the global selected_client variable
    
    # Clear the client list frame
    for widget in client_frame.winfo_children():
        widget.destroy()

    # Add the label for connected clients
    label_clients = ctk.CTkLabel(master=client_frame, text="Connected clients", font=("Arial", 18))
    label_clients.pack(pady=10)

    # Get the list of clients from the server
    clients = server.list_all_clients()

    # Reset selected_client variable to ensure a new selection can be made
    selected_client.set(0)

    # List all clients with checkboxes
    for idx, client in enumerate(clients, start=1):  # Start client ID from 1
        checkbox = ctk.CTkRadioButton(master=client_frame, text=client, variable=selected_client, value=idx)
        checkbox.pack(anchor="w", padx=10, pady=5)

    # Add the refresh button to update the client list
    refresh_button = ctk.CTkButton(master=client_frame, text="Refresh", command=list_clients)
    refresh_button.pack(pady=10)

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
b_livefeed = ctk.CTkButton(master=actions_frame, text="View Live Feed", command=lambda: send_action_to_selected_client("LIVEFEED"))
b_livefeed.pack(pady=5)

b_viewfaces = ctk.CTkButton(master=actions_frame, text="View Faces", command=lambda: send_action_to_selected_client("VIEWFACES"))
b_viewfaces.pack(pady=5)

b_downlog = ctk.CTkButton(master=actions_frame, text="Download Log", command=lambda: send_action_to_selected_client("DOWNLOADLOG"))
b_downlog.pack(pady=5)

b_downdata = ctk.CTkButton(master=actions_frame, text="Download all Data", command=lambda: send_action_to_selected_client("DOWNLOADALL"))
b_downdata.pack(pady=5)

b_shutdowncam = ctk.CTkButton(master=actions_frame, text="Shutdown Camera", command=lambda: send_action_to_selected_client("SHUTDOWN"))
b_shutdowncam.pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
