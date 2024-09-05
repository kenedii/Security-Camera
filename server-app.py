import customtkinter as ctk
import asyncio
import server
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Initialize the Tkinter root
root = ctk.CTk()
root.title("123SecurityCam - Server App")
root.geometry("800x600")

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
    
    # Show the client frame and list clients
    client_frame.pack(side="left", fill="y", padx=20, pady=20)
    list_clients()

def on_close_server():
    # Schedule the coroutine to close the server
    asyncio.run_coroutine_threadsafe(server.close_server(server_instance), loop)

    # Hide the close button and show the start button
    b_closeserver.pack_forget()
    b_startserver.pack(pady=12, padx=10)
    
    # Hide the client frame
    client_frame.pack_forget()

def list_clients():
    # Clear the client list frame
    for widget in client_frame.winfo_children():
        widget.destroy()

    # Add the label
    label_clients = ctk.CTkLabel(master=client_frame, text="Connected clients", font=("Arial", 18))
    label_clients.pack(pady=10)

    # Get the list of clients from the server
    clients = server.list_all_clients()

    # List all clients with checkboxes
    for client in clients:
        client_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(master=client_frame, text=client, variable=client_var)
        checkbox.pack(anchor="w", padx=10, pady=5)

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

# Action buttons - when server is on these will appear
b_livefeed = ctk.CTkButton(master=frame, text="View Live Feed", command=on_start_server)
b_viewfaces = ctk.CTkButton(master=frame, text="View Faces", command=on_start_server)
b_downlog = ctk.CTkButton(master=frame, text="Download Log", command=on_start_server)
b_downdata = ctk.CTkButton(master=frame, text="Download all Data", command=on_start_server)
b_shutdowncam = ctk.CTkButton(master=frame, text="Shutdown Camera", command=on_start_server)

# Run the Tkinter main loop
root.mainloop()
