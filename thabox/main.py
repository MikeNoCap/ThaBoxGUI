import threading
import socketio
import tkinter as tk
from PIL import Image, ImageTk
import asyncio
import textwrap

messages = []
socket_thread = None


sio = socketio.AsyncClient()
SERVER_ADDRESS = ["http://localhost:8000", "http://thabox.asmul.net:8080"][0]

CONNECTED = False
USERNAME = ""
ROOM = ""

EXIT = False

root = tk.Tk()
root.geometry("500x692")
root.title("ThaBox")
root.iconbitmap("thabox\icon.ico")


img = Image.open("thabox\ThaBox.png")
img = img.resize((500, 500))
tkimage = ImageTk.PhotoImage(img)





        
def on_closing():
    global EXIT
    EXIT = True
    root.destroy()
    

logo = tk.Label(image=tkimage, borderwidth=0)
logo.grid(row=0, column=0)

input_frame = tk.Frame(root, background="black")



room_label = tk.Label(input_frame, text="Room-name:", background="cyan", font="Haettenschweiler 18")
room_entry = tk.Entry(input_frame, font="Haettenschweiler 18")

username_label = tk.Label(input_frame, text="Username:    ", background="magenta", font="Haettenschweiler 18")
username_entry = tk.Entry(input_frame, font="Haettenschweiler 18")


error_message = tk.Label(root, text="\n", background="black", font="Courier 25")
error_message.configure(foreground="red")


@sio.event 
async def receive_message(data):
    global ROOM, messages, msgs, rows_used, message_boxes
    if data["room_name"] == ROOM:
        rows_used += len(data["message"].splitlines())
        while rows_used > 14:
            msg_box = message_boxes.pop(0)
            text = msg_box[2].cget("text")
            msg_box[0].destroy()
            rows_used -= len(text.splitlines())
        
        
        messages.append((data['username'], data['message']))
        
        if data["is_server"]:
            msg_frame = tk.Frame(msgs, background="black")
            message = tk.Label(msg_frame, background="black", foreground="white", text=data['message'], font="Haettenschweiler 18")
            message.grid(row=0, column=1, sticky="W", padx=5, pady=5)
            msg_frame.grid(row=len(messages), column=0)
            message_boxes.append((msg_frame, "SERVER", message))
            return

        msg_frame = tk.Frame(msgs, background="black")
        author = tk.Label(msg_frame, background="magenta", foreground="black", text=data['username'], font="Haettenschweiler 18")
        message = tk.Label(msg_frame, background="cyan", foreground="black", text=data['message'], font="Haettenschweiler 18")
        author.grid(row=0, column=0, sticky="E", pady=5)
        message.grid(row=0, column=1, sticky="W", padx=5, pady=5)
        msg_frame.grid(row=len(messages), column=0)
        message_boxes.append((msg_frame, author, message))


async def send_message(username, room_name, message):
    if (message_text := message.get()) == "":
        return
    if message_text.isspace():
        message.delete(0, tk.END)
        return
    if len(message_text) > 81:
        message_error = tk.Label(message_input, text="Message too long!", background="red", font="Haettenschweiler 16")
        message_error.grid(row=0, column=0, sticky="s")
        message_input.update()
        await asyncio.sleep(1)
        message_error.destroy()
        return message.delete(0, tk.END)
    await sio.emit("send_message", data={"is_server": False, "username": username, "room_name": room_name, "message": "\n".join(textwrap.wrap(message_text, 27))})
    message.delete(0, tk.END)


async def server_message(data):
    await sio.emit("send_message", data=data)


async def chat_room(username, room_name):
    global messages, msgs, rows_used, message_boxes, message_input
    globals().update(USERNAME=username)
    globals().update(ROOM=room_name)

    logo.destroy()
    input_frame.destroy()
    join_button.destroy()
    error_message.destroy()
    
    message_boxes = []
    rows_used = 0

    
    
    message_input = tk.Frame(root, background="red")
    
    message_entry = tk.Entry(message_input, font="Haettenschweiler 19", width=23)
    loop = asyncio.new_event_loop()
    message_entry.bind('<Return>', lambda event: loop.run_until_complete(send_message(username, room_name, message_entry)))
    message_send_button = tk.Button(message_input, font="Haettenschweiler 20", background="red",text="Send", command=lambda: loop.run_until_complete(send_message(username, room_name, message_entry)))


    msgs = tk.Frame(root, background="black")
    msgs.grid(row=0, column=0)

    

    
    message_entry.grid(row=1, column=0, padx=10)
    message_send_button.grid(row=1, column=1)
    message_input.grid(row=1, column=0)
    
    await server_message({"is_server": True, "username": "SERVER", "room_name": room_name, "message": f"{username} joined the box"})
    while True:
        global EXIT 
        if EXIT:
            await server_message({"is_server": True, "username": "SERVER", "room_name": room_name, "message": f"{username} left the box"})
            await asyncio.sleep(2)
            await sio.disconnect()
            await sio.wait()
            return
            
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
    global socket_thread
    username = username_entry.get()
    room_name = room_entry.get()
    if username == "": 
        return set_error_text("Please enter a\nusername first")
    if len(username) < 3 or len(username) > 16:
        username_entry.delete(0, tk.END)
        return set_error_text("Username should be\n3-16 characters")
    if len(room_name) == 0:
        return set_error_text("Room name can't\nbe empty")
    
    socket_thread = threading.Thread(target=lambda: asyncio.run(connect_server(username, room_name)), daemon=True)
    socket_thread.start()

join_button = tk.Button(root, text="Join/Create box", padx=70, pady=14, font="Haettenschweiler 21", background="#b40000", command=join_create)


username_label.grid(row=1, column=2, ipady=5, pady=5, sticky="e")#, sticky="n")
username_entry.grid(row=1, column=3, ipady=7, pady=5)#, sticky="n")

room_label.grid(row=1, column=4, ipady=5, pady=5, sticky="e")#, sticky="w")
room_entry.grid(row=1, column=5, ipady=7, pady=5)#, sticky="w")

join_button.grid(row=2, column=0)


input_frame.grid(row=1, column=0)

error_message.grid(row=3, column=0)




root.protocol("WM_DELETE_WINDOW",on_closing)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(background='black')
root.configure(highlightthickness=0)
root.resizable(False, False)
root.attributes('-topmost', True)




def start():
    root.mainloop() 

if __name__ == '__main__':
    start()
