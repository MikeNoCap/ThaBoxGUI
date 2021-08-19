from client import SERVER_ADDRESS
import socketio
import tkinter as tk
from PIL import Image, ImageTk


messages = ["\n" for i in range(10)]

sio = socketio.Client()
SERVER_ADDRESS = "http://0.0.0.0:8000"
sio.connect(SERVER_ADDRESS)


root = tk.Tk()

root.title("ThaBox")
root.iconbitmap("icon.ico")


img = Image.open("ThaBox.png")
img = img.resize((500, 500))
tkimage = ImageTk.PhotoImage(img)

join_button_img = Image.open("button.png")
join_button_tkimage = ImageTk.PhotoImage(join_button_img)



def box_chat(username, room_name):
    global message
    input_frame.destroy()
    join_button.destroy()
    logo.destroy()
    error_message.destroy()
    message = tk.Label(root, text="Test")
    message.grid(row=0, column=0)


        
    

def on_closing():
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


def set_error_text(text):
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
    
    try:

        
        return box_chat(username, room_name)
    except socketio.exceptions.ConnectionError as e:
        return set_error_text("Could not connect\nto server")

join_button = tk.Button(root, text="Join/Create box", padx=70, pady=14, font="Haettenschweiler 21", background="#b40000", command=join_create)


username_label.grid(row=1, column=2, ipady=5)#, sticky="n")
username_entry.grid(row=1, column=3, ipady=7)#, sticky="n")

room_label.grid(row=1, column=4, ipady=5)#, sticky="w")
room_entry.grid(row=1, column=5, ipady=7)#, sticky="w")

join_button.grid(row=2, column=0)


input_frame.grid(row=1, column=0)

error_message.grid(row=3, column=0)


@sio.event
def message(data):
    print('I received a message!')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(background='black')
root.configure(highlightthickness=0)
root.attributes('-topmost', True)
root.mainloop()