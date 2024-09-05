import customtkinter as ctk
import asyncio
import server
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Initialize the Tkinter root
root = ctk.CTk()
root.title("123SecurityCam - Server App")
root.geometry("500x350")

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def on_start_server():
    # Schedule the coroutine to be executed
    asyncio.run_coroutine_threadsafe(server.start_server(), loop)

# Create an event loop for the background thread
loop = asyncio.new_event_loop()
threading.Thread(target=start_event_loop, args=(loop,), daemon=True).start()

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="123SecurityCam - Server App", font=("Arial", 24))
label.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text="Start Server", command=on_start_server)
button.pack(pady=12, padx=10)

# Run the Tkinter main loop
root.mainloop()
