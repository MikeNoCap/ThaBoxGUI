import threading
import socketio
import tkinter as tk
from PIL import Image, ImageTk
import asyncio

messages = ["\n" for i in range(10)]



sio = socketio.AsyncClient()
SERVER_ADDRESS = ["http://localhost:8000", "http://thabox.asmul.net:8080"][1]

CONNECTED = False
USERNAME = ""
ROOM = ""

root = tk.Tk()

root.title("ThaBox")
root.iconbitmap("icon.ico")


img = Image.open("ThaBox.png")
img = img.resize((500, 500))
tkimage = ImageTk.PhotoImage(img)



def box_chat(username, room_name):
    global message
    input_frame.destroy()
    join_button.destroy()
    logo.destroy()
    error_message.destroy()
    message = tk.Label(root, text="Test")
    message.grid(row=0, column=0)


        
    

async def on_closing():
    await sio.disconnect()
    root.destroy()

logo = tk.Label(image=tkimage, borderwidth=0)
logo.grid(row=0, column=0)

input_frame = tk.Frame(root, background="black")



room_label = tk.Label(input_frame, text="Room-name:", background="cyan", font="Haettenschweiler 14")
room_entry = tk.Entry(input_frame, width=23)

username_label = tk.Label(input_frame, text="Username:    ", background="magenta", font="Haettenschweiler 14")
username_entry = tk.Entry(input_frame, width=23)


error_message = tk.Label(root, text="\n", background="black", font="Courier 25")
error_message.configure(foreground="red")


@sio.event
async def receive_message(data):
    global ROOM, messages, USERNAME
    if data["room_name"] == ROOM:
        prev_messages = messages.cget("text")
        messages.configure(text=f"{prev_messages}{data['username']}: {data['message']}\n")


async def send_message(username, room_name, message):
    await sio.emit("send_message", data={"username": username, "room_name": room_name, "message": message})


async def chat_room(username, room_name):
    global messages, message_entry
    globals().update(USERNAME=username)
    globals().update(ROOM=room_name)

    logo.destroy()
    input_frame.destroy()
    join_button.destroy()
    error_message.destroy()

    message_input = tk.Frame(root, background="black")
    message_entry = tk.Entry(message_input)
    loop = asyncio.new_event_loop()
    message_send_button = tk.Button(message_input, text="Send", command=lambda: loop.run_until_complete(send_message(username, room_name, message_entry.get())))

    messages = tk.Label(root, text="", background="black", foreground="cyan", font="Haettenschweiler 16")
    
    messages.grid(row=0)

    message_entry.grid(row=0, column=0)
    message_send_button.grid(row=0, column=1)
    message_input.grid(row=1, column=0)

    while True:
        await asyncio.sleep(0.3)


async def connect_server(username, room_name):
    set_error_text("Connecting to server\n", "white")
    connected = False
    while not connected:
        try:
            await sio.connect(SERVER_ADDRESS)
            globals().update(CONNECTED=True)
            set_error_text("Connected!\n", "green")
            connected = True
        except socketio.exceptions.ConnectionError:
            set_error_text("Failed to \nconnect to server")
            await asyncio.sleep(4)
            set_error_text("Retrying\n", "yellow")
    await asyncio.sleep(2)

    set_error_text("Joining room\n", "white")
    await sio.emit("join_room", {"room_name": room_name})
    await asyncio.sleep(1)
    set_error_text("Joined room!\n", "green")
    await chat_room(username, room_name)


def set_error_text(text, color="red"):
    error_message.configure(foreground=color)
    return error_message.config(text=text)


def join_create():
    username = username_entry.get()
    room_name = room_entry.get()
    if username == "":
        return set_error_text("Please enter a\nusername first")
    if len(username) < 3 or len(username) > 16:
        return set_error_text("Username should be\n3-16 characters")
    if len(room_name) == 0:
        return set_error_text("Room name can't\nbe empty")
    
    threading.Thread(target=lambda: asyncio.run(connect_server(username, room_name))).start()

join_button = tk.Button(root, text="Join/Create box", padx=70, pady=14, font="Haettenschweiler 21", background="#b40000", command=join_create)


username_label.grid(row=1, column=2, ipady=5)#, sticky="n")
username_entry.grid(row=1, column=3, ipady=7)#, sticky="n")

room_label.grid(row=1, column=4, ipady=5)#, sticky="w")
room_entry.grid(row=1, column=5, ipady=7)#, sticky="w")

join_button.grid(row=2, column=0)


input_frame.grid(row=1, column=0)

error_message.grid(row=3, column=0)



loop = asyncio.get_event_loop()
root.protocol("WM_DELETE_WINDOW",lambda: loop.run_until_complete(on_closing()))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(background='black')
root.configure(highlightthickness=0)
root.attributes('-topmost', True)





root.mainloop() # THREADING WILL SOLVE ALL OF MY PROBLEMS: