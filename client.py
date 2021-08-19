# Client
import asyncio
import socketio
import keyboard
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
import sys
import os
import string
import random
import time
import re
from hashlib import sha256

try:
    import utils
    import main as main_navigation
    from utils import clear, User, Preferences
    import rendering
except ModuleNotFoundError:
    import thabox.utils as utils
    import thabox.main as main_navigation
    from thabox.utils import clear, User, Preferences
    import thabox.rendering as rendering


class MessagePromptStop(Exception):
    pass


sio = socketio.AsyncClient(request_timeout=30)

console = Console()


CONNECTED: bool = False
SERVER_ADDRESS = ("http://localhost:8000", "http://thabox.asmul.net:8000")[1]

USERNAME = ""
ROOM = ""
ROOMS: list = []
ROOM_WORKS : bool = False
WAIT_FOR_INFO = False
LOGIN_DATA = 0

messages_to_show: list = []

printable_chars = list(string.printable.replace("\n", "").replace(" ", "").replace("    ", ""))
def add_salt(hash_no_salt):
    for i in range(9):
        hash_no_salt += random.choice(printable_chars)
    return hash_no_salt


def exit_anim():
    print_string = "[a]Hope[/][b] you[/][a] had[/][b] a[/][a] great[/][b] time![/]"
    s1 = print_string.replace("[a]", "[cyan]").replace("[b]", "[magenta]")
    s2 = print_string.replace("[a]", "[magenta]").replace("[b]", "[cyan]")


    frames = []

    extra = ""
    s = ""

    for i in range(30):
        x = s1 if i % 2 == 0 else s2
        frames.append(Panel(extra+s+x, height=32, width=90))
        s += " "
        extra += "\n"
    for i in range(30):
        x = s1 if i % 2 == 0 else s2
        s+=" "
        extra = extra[:-1]
        frames.append(Panel(extra+s+x, height=32, width=90))
    frames.append(Panel("", height=32, width=90))
    console = Console()
    os.system("cls" if os.name == "nt" else "clear")


    with Live(refresh_per_second=10) as l:
        for i in frames:
            time.sleep(0.15)
            l.update(i)

    sys.exit(1)


def remove_salt(hash_and_salt):
    back_hash_removed = hash_and_salt[:-9]
    return back_hash_removed


def hash_pass(passwrd: str):
    hashed = sha256(bytes(passwrd, "utf8")).hexdigest()
    return add_salt(hashed)


async def create_account(username: str, password: str):
    password = hash_pass(password)
    prefs = Preferences()
    user_ob = User(username=username, paswrd=password, preferences=prefs)
    await save_user(username, password, prefs.preference_dict)
    return user_ob


async def sign_up():
    global secrets
    progress_visual = []
    username_status = "working"
    while username_status != "ready":
        clear()
        console.print(Panel(Text.assemble(("Enter a username", "bold purple")),
                            style="bold purple", border_style="bold purple"))

        username = Prompt.ask(Text.assemble(("╰→", "bold red")))
        console.print("Checking username...", style="bold yellow")
        data = await get_user_data(username)

        if data is not None:
            clear()
            console.print(Panel(Text.assemble(("Username already taken", "bold purple")),
                                style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if " " in username:
            clear()
            console.print(Panel(Text.assemble(("Can not have space in username", "bold purple")),
                                style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if "[" in username or "]" in username:
            clear()
            console.print(Panel(Text.assemble(("Username must not contain square-brackets ('[', ']')",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(3.1)
            clear()
            continue
        if len(username) < 4:
            clear()
            console.print(Panel(Text.assemble(("Username must be at least 4 characters long",
                                               "bold purple")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue

        progress_visual.append(Panel(Text.assemble(("Username ☺", "bold green")),
                                     style="bold green", border_style="bold green"))
        progress_visual.append(Text.assemble(("╰→", "bold red"), (username, "none")))
        username_status = "ready"

    password_status = "working"
    while password_status != "ready":
        clear()
        for i in progress_visual:
            console.print(i)

        console.print(Panel(Text.assemble(("Enter a password (1)", "bold cyan")),
                            style="bold cyan", border_style="bold cyan"))
        password = Prompt.ask(Text.assemble(("╰→", "bold red")), password=True)
        console.print("Checking password...", style="bold yellow")
        await asyncio.sleep(0.3)
        # Checks
        if " " in password:
            clear()
            console.print(Panel(Text.assemble(("Can not have space in password", "bold cyan")),
                                style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if len(password) < 8:
            clear()
            console.print(Panel(Text.assemble(("Password must be at least 8 characters long",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if len(password) > 32:
            clear()
            console.print(Panel(Text.assemble(("Password can not be any longer than 32 characters",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if not re.search("[a-z]", password):
            clear()
            console.print(Panel(Text.assemble(("Password must contain at least one lowercase character",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if not re.search("[A-Z]", password):
            clear()
            console.print(Panel(Text.assemble(("Password must contain at least one uppercase character",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if not re.search("[A-Z]", password):
            clear()
            console.print(Panel(Text.assemble(("Password must contain at least one uppercase character",
                                               "bold cyan")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        if not re.search("[0-9]", password):
            clear()
            console.print(Panel(Text.assemble(("Password must contain at least one digit", "bold cyan")),
                                style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue
        for i in password:
            if i not in printable_chars:
                clear()
                console.print(Panel(Text.assemble(("Password can only contain letters from the ASCII table",
                                                   "bold cyan")), style="bold red", border_style="bold red"))
                await asyncio.sleep(2.1)
                clear()
                continue
        clear()
        for i in progress_visual:
            console.print(i)
        console.print(Panel(Text.assemble(("Enter a password (1)", "bold cyan")),
                            style="bold cyan", border_style="bold cyan"))
        console.print(Text.assemble(("╰→", "bold red")))

        console.print(Panel(Text.assemble(("Repeat password (2)", "bold cyan")),
                            style="bold cyan", border_style="bold cyan"))
        password2 = Prompt.ask(Text.assemble(("╰→", "bold red")), password=True)

        if password != password2:
            clear()
            console.print(Panel(Text.assemble(("Passwords did not match", "bold cyan")),
                                style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            clear()
            continue

        progress_visual.append(Panel(Text.assemble(("Password ☺", "bold green")),
                                     style="bold green", border_style="bold green"))
        progress_visual.append(Text.assemble(("╰→", "bold red"), ("HIDDEN", "bold yellow")))
        password_status = "ready"
    clear()
    for i in progress_visual:
        console.print(i)

    a = await create_account(username, password2)

    console.print(Panel(Text.assemble(("Successfully created an account!")), style="bold green", border_style="green"))
    await asyncio.sleep(2.1)
    clear()
    return a


async def log_in():
    status = "working"
    while status != "done":
        clear()
        console.print(Panel(Text.assemble(("Username", "bold purple")),
                            style="bold magenta", border_style="bold purple"))
        username = Prompt.ask(Text.assemble(("╰→", "bold red")))

        console.print(Panel(Text.assemble(("Password", "bold purple")), style="bold cyan", border_style="bold cyan"))
        password = Prompt.ask(Text.assemble(("╰→", "bold red")), password=True)

        console.print("Validating login...", style="bold yellow")
        user_data = await get_user_data(username)

        if user_data is None:
            clear()
            console.print(Panel(Text.assemble(("Invalid username or password. Please try again.",
                                               "bold red")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            continue

        if not sha256(bytes(password, "utf-8")).hexdigest() == remove_salt(user_data[1]):
            clear()
            console.print(Panel(Text.assemble(("Invalid username or password. Please try again.",
                                               "bold red")), style="bold red", border_style="bold red"))
            await asyncio.sleep(2.1)
            continue
        clear()
        console.print(Panel(Text.assemble(("Success! Logged in as " + username, "bold green")),
                            style="bold green", border_style="green"))
        await asyncio.sleep(2.1)
        clear()
        prefs = Preferences()
        new_pref_dict = {
            "Name Colour": user_data[2],
            "Message Colour": user_data[3],
            "Border Colour": user_data[4],
            "Message Border Colour": user_data[5]
        }
        prefs.preference_dict = new_pref_dict
        return User(username, hash_pass(password), prefs)


async def login():
    choice = utils.make_style_prompt(choices=["Log in", "Sign up"], prompt_msg="Please log-in/sign up:",
                                     main_style="bold purple", frame_border_style="bold cyan", frame_style="bold red")
    if choice == "Log in":
        return await log_in()
    if choice == "Sign up":
        return await sign_up()


async def exit_client():
    await sio.disconnect()
    exit()


def set_rooms(data):
    globals().update(ROOMS=data["rooms"])


async def get_rooms():
    await sio.emit("get_rooms", callback=set_rooms)


@sio.event
def set_user_data(data):
    if data["sid"] != sio.sid:
        return
    globals().update(LOGIN_DATA=data["info"])
    globals().update(WAIT_FOR_INFO=False)


async def update_user(user: User):
    prefs = user.preferences.preference_dict
    username = user.username
    password = user.hashed_pass
    
    success = False
    breakcount = 0
    breakcount += 1
    while not success:    
        try:
            await sio.emit("update_user", {"username": username, "passwrd": password, "prefs": prefs})
            success = True
        except socketio.exceptions.BadNamespaceError:
            try:
                await sio.connect(SERVER_ADDRESS)
            except socketio.exceptions.ConnectionError:
                feedback = Panel("Lost connection and could not reconnect. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
                console.print(feedback)
        if breakcount == 80:
            feedback = Panel("Failed to communicate with server, your newly set preferences will not be saved", style="bold red", border_style="yellow")
            console.print(feedback)
            await asyncio.sleep(3)
            clear()
            return
        await asyncio.sleep(0.1)
        continue



async def get_user_data(username):
    globals().update(WAIT_FOR_INFO=True)
    success = False
    breakcount = 0
    while not success:
        breakcount += 1
        try:
            await sio.emit("get_user_data", {"to_access": username, "sid": sio.sid})
            await asyncio.sleep(1)
            success = True
        except socketio.exceptions.BadNamespaceError:
            try:
                await sio.connect(SERVER_ADDRESS)
            except socketio.exceptions.ConnectionError:
                feedback = Panel("Lost connection and could not reconnect. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
                console.print(feedback)
        if breakcount == 80:
            feedback = Panel("Failed to communicate with server, please try logging in again.", style="bold yellow", border_style="yellow")
            console.print(feedback)
            await asyncio.sleep(3)
            clear()
            return await login()
        await asyncio.sleep(0.1)
        continue

            
    
    while True:
        await asyncio.sleep(0.7)
        global WAIT_FOR_INFO
        if not WAIT_FOR_INFO:
            break
    global LOGIN_DATA
    info = LOGIN_DATA
    globals().update(LOGIN_DATA=0)
    return info


async def save_user(username, password, pref_dict):
    breakcount = 0
    success = False
    while not success:
        breakcount += 1
        try:
            await sio.emit("save_user", {"username": username, "password": password, "pref_dict": pref_dict})
            success = True
        except socketio.exceptions.BadNamespaceError:
            try:
                await sio.connect(SERVER_ADDRESS)
            except socketio.exceptions.ConnectionError:
                feedback = Panel("Lost connection and could not reconnect. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
                console.print(feedback)
            continue
        if breakcount == 80:
            feedback = Panel("Failed to communicate with server, please try signing up again.", style="bold yellow", border_style="yellow")
            console.print(feedback)
            await asyncio.sleep(3)
            clear()
            return await login()
        await asyncio.sleep(0.1)
        continue
    


def get_room_data():
    return ROOMS


@sio.event
async def connect():
    globals().update(CONNECTED=True)


@sio.event
async def disconnect():
    globals().update(ROOM_WORKS=False)
    globals().update(CONNECTED=False)


@sio.event
async def send_message(sid, data):
    return #print(f'[CLIENT]: message sent {sid}, data: {data}')


@sio.event
async def receive_message(data):
    global messages_to_show, ROOM, USERNAME
    if data["room_name"] == ROOM:
        if USERNAME != data["username"]:
            messages_to_show.append([data["username"], data["message"]])


async def main():
    console.print(Panel("Starting connection...", style="bold yellow", border_style="bold yellow"))
    try:
        await sio.connect(SERVER_ADDRESS)
    except socketio.exceptions.ConnectionError as e:
        feedback = Panel("Could not connect to server. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
        console.print(feedback)
        exit()

    console.print(Panel('Connected!', style="bold green", border_style="bold green"))
    console.print(Panel("Enjoy your stay!", style="bold green", border_style="bold green"))
   
    #await rendering.load_box_animation(None)
    return await console_loop()


async def ping_server():
    await sio.emit("keep_alive")


async def console_loop(user=None):
    global messages_to_show
    clear()
    if user is None:
        action, user = await main_navigation.main_menu(logged_in=False, logged_in_as=None)
    if user is not None:
        action, user = await main_navigation.main_menu(logged_in=True, logged_in_as=user)
    
    if user is not None:
        await update_user(user)

    if action == "exit":
        if user is not None:
            await update_user(user)        
            await asyncio.sleep(1)
            print("Saving account preferences...")
        try:
            await sio.disconnect()
        except:
            pass
        await sio.wait()
        return
    if action == "login":
        user = await login()
        return await console_loop(user=user)
    globals().update(USERNAME=user.username)
    

    console.print(Panel("Enter the name of a box to join \nIf the box doesn't exist a new one will be created", style=user.preferences.preference_dict["Border Colour"], border_style=user.preferences.preference_dict["Border Colour"]))
    name = Prompt.ask(Text.assemble(("╰>", user.preferences.preference_dict["Border Colour"])))
    console.print(Panel(f"Joining {name}", style="green", border_style="green"))
    await asyncio.sleep(1)
    globals().update(ROOM=name)
    globals().update(ROOM_WORKS=True)
    clear()
        
        

    cancel_render = False
    while True:
        if not cancel_render:
            console.print(await rendering.render_menu_screen(await rendering.get_message_box_rows([], user)))
        else:
            cancel_render = False

        
        wait = True
        while wait:
            if not ROOM_WORKS: # Check if connection was lost to reconnect if it was try to reconnect.
                console.print(Panel("Your connection was lost.", style="bold yellow", border_style="bold yellow"))
                console.print(Panel("Reconnecting...", style="bold yellow", border_style="bold yellow"))


                loop_count = 0 # Store loop-count to cancel reconnect if it exceeds time-limit.
                feedback = Panel("Could not reconnect. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
                back_online = False
                
                reconnecting = True
                while reconnecting:
                    await asyncio.sleep(1)
                
                    loop_count += 1
                    if loop_count == 11:
                        break

                    try:
                        await sio.emit("join_room", {"username": user.username, "room_name": name, "sid": sio.sid})
                    except Exception as e:
                        continue
                
                    feedback = Panel("Back online!", style="bold green", border_style="bold green")
                    reconnecting = False
                    back_online = True
                    globals().update(ROOM_WORKS=True)
                console.print(feedback)

                if back_online:
                    clear()
                    console.print(await rendering.render_menu_screen(await rendering.get_message_box_rows([], user)))

            
            if keyboard.is_pressed("ctrl+space"):
                event = "msg"
                break
            if keyboard.is_pressed("ctrl+alt"):
                event = "return"
                break
            global messages_to_show
            if len(messages_to_show) != 0:
                clear()
                index_of_i = -1
                for i in messages_to_show:
                    index_of_i += 1
                    with Live("", refresh_per_second=14) as live:
                        render_user = User(i[0], "NotImportant", preferences=user.preferences)
                        await rendering.render_message(i[1], render_user, live=live)
                        messages_to_show.pop(index_of_i)
                clear()
                console.print(await rendering.render_menu_screen(await rendering.get_message_box_rows([], user)))
                
            await asyncio.sleep(0.2)
        if event == "msg":
            clear()
            message = await rendering.prompt(user)
            clear()
            if not ROOM_WORKS: # Check if connection was lost to reconnect if it was try to reconnect.
                console.print(Panel("Your connection was lost.", style="bold yellow", border_style="bold yellow"))
                console.print(Panel("Reconnecting...", style="bold yellow", border_style="bold yellow"))


                loop_count = 0 # Store loop-count to cancel reconnect if it exceeds time-limit.
                feedback = Panel("Could not reconnect. Please check your internet connection and restart the program.", style="bold red", border_style="bold red")
                back_online = False
                
                reconnecting = True
                while reconnecting:
                    await asyncio.sleep(1)
                
                    loop_count += 1
                    if loop_count == 11:
                        break

                    try:
                        await sio.emit("join_room", {"username": user.username, "room_name": name, "sid": sio.sid})
                    except Exception as e:
                        continue
                
                    feedback = Panel("Back online!", style="bold green", border_style="bold green")
                    reconnecting = False
                    back_online = True
                    globals().update(ROOM_WORKS=True)
                console.print(feedback)
                if back_online:
                    clear()
                    console.print(await rendering.render_menu_screen(await rendering.get_message_box_rows([], user)))
            await sio.emit("send_message", {"username": user.username, "message": message, "room_name": name})
            await asyncio.sleep(0.2)
            with Live("", refresh_per_second=14) as live:
                render_user = User(USERNAME, "NotImportant", preferences=user.preferences)
                await rendering.render_message(message, render_user, live=live)
                live.update(Text.assemble(await rendering.render_menu_screen(await rendering.get_message_box_rows([], user)), ("\nTips: Hold ctrl+space to type, Hold ctrl+alt to go back to main-menu.")))
            cancel_render = True
            
        if event == "return":
            await sio.emit("leave_room", {"username": user.username, "room_name": name})
            await asyncio.sleep(0.2)
            return await console_loop(user)

def start():
    try:
        asyncio.run(main())
        exit_anim()
    except RuntimeError:
        pass

if __name__ == "__main__":
    start()