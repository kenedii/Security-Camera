import customtkinter as ctk
import asyncio
import client
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Initialize the Tkinter root
root = ctk.CTk()
root.title("123SecurityCam - Client App")
root.geometry("800x600")

client_instance = None

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def on_start_client():
    global client_instance
    # Schedule the coroutine to start the client
    future = asyncio.run_coroutine_threadsafe(client.start_client(), loop)  # Assuming no file path
    client_instance = future  # Store the future task of the client
    
    # Hide the start button after the client is started
    b_startclient.pack_forget()
    b_closeclient.pack(pady=12, padx=10)

def on_close_client():
    global client_instance
    if client_instance:
        # Schedule the coroutine to close the client connection
        asyncio.run_coroutine_threadsafe(client_instance.result().close(), loop)
    
    # Hide the close button after the client is closed
    b_closeclient.pack_forget()
    b_startclient.pack(pady=12, padx=10)

# Create an event loop for the background thread
loop = asyncio.new_event_loop()
threading.Thread(target=start_event_loop, args=(loop,), daemon=True).start()

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="123SecurityCam - Client App", font=("Arial", 24))
label.pack(pady=12, padx=10)

b_startclient = ctk.CTkButton(master=frame, text="Start Client", command=on_start_client)
b_startclient.pack(pady=12, padx=10)

b_closeclient = ctk.CTkButton(master=frame, text="Close Client", command=on_close_client)

# Run the Tkinter main loop
root.mainloop()
