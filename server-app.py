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
    
    # Hide the start button after the server is started
    b_startserver.pack_forget()
    b_closeserver.pack(pady=12, padx=10)

def on_close_server():
    # Schedule the coroutine to close the server
    asyncio.run_coroutine_threadsafe(server.close_server(server_instance), loop)

    # Hide the close button after the server is closed
    b_closeserver.pack_forget()
    b_startserver.pack(pady=12, padx=10)

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

# Action buttons - when server is on these will appear
b_livefeed = ctk.CTkButton(master=frame, text="View Live Feed", command=on_start_server)
b_viewfaces = ctk.CTkButton(master=frame, text="View Faces", command=on_start_server)
b_downlog = ctk.CTkButton(master=frame, text="Download Log", command=on_start_server)
b_downdata = ctk.CTkButton(master=frame, text="Download all Data", command=on_start_server)
b_shutdowncam = ctk.CTkButton(master=frame, text="Shutdown Camera", command=on_start_server)


# Run the Tkinter main loop
root.mainloop()
