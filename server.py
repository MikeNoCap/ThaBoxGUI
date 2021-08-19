# Server
import socketio
from aiohttp import web
from fastapi import FastAPI
# Configure server app
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid):
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect(sid):
    print("I'm disconnected!")
    
