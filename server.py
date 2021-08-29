# Server
import socketio


sio = socketio.AsyncServer(async_mode="asgi", ping_interval=30, ping_timeout=4294967)
app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid):
    print(f"[SERVER]: connect {sid}")


@sio.event
async def disconnect(sid):
    print(f"[SERVER]: disconnect {sid}")

    

@sio.event
async def join_room(sid, data):
    global room_data
    sio.enter_room(sid, data['room_name'])
    print(f"{sid} joined to {data['room_name']}")
    


@sio.event
async def leave_room(sid, data):
    print(f"{data['username']} left {data['room_name']}")
    sio.leave_room(sid, data['room_name'])
    

@sio.event
async def send_message(sid, data):
    print(f"[SERVER]: send message {sid}, data: {data}")
    await sio.emit("receive_message", data, room=data["room_name"])