import json
from time import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4, UUID
from typing import Dict, List, Optional, Tuple

import BoardState
from GameRoom import GameRoom, Message
from Player import Player

app = FastAPI()


class CreatePlayerRequest(BaseModel):
    player_name: str


class CreateRoomRequest(BaseModel):
    player_id: str


class JoinRoomRequest(BaseModel):
    player_id: str
    room_id: str


class MessageRequest(BaseModel):
    room_id: str
    player_id: str
    message: str


class MakeMoveRequest(BaseModel):
    room_id: str
    player_id: str
    row: int
    column: int
    puck: int


# --- Game State ---


# --- In-Memory Data ---

players: Dict[str, Player] = {} # <id, player object>
rooms: Dict[str, GameRoom] = {} # <id, room object>


def get_room(room_id: str) -> GameRoom:
    room = rooms.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found!")
    return room


def get_player(player_id: str) -> Player:
    if player_id in players:
        return players[player_id]
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found!")


# --- API Endpoints ---

@app.put("/createPlayer")
def create_player(req: CreatePlayerRequest):
    player_name = req.player_name
    random_id = str(uuid4())
    new_player = Player(player_id=random_id, player_name=player_name)
    players[random_id] = new_player
    print(f"Created new player: {new_player}")
    return {
        "response": {
            "player_id": random_id
        }
    }


@app.get("/listPlayers")
def list_players():
    player_json = [json.loads(str(player)) for player in players.values()]
    print(f"Players: {player_json}")
    return {
        "response": {
            "players": player_json
        }
    }

@app.get("/playerName")
def player_name(id: str):
    return {
        "response": {
            "player_name": players[id].player_name if id in players else ""
        }
    }


@app.put("/createRoom")
def create_room(req: CreateRoomRequest):
    player_id = req.player_id
    if player_id not in players:
        raise HTTPException(status_code=404, detail=f"Cannot create room, player id: {player_id} not found.")
    room = GameRoom(player_id)
    room_id = str(room.room_id)
    rooms[room_id] = room
    return {
        "response": {
            "room_id": room_id
        }
    }


@app.post("/joinRoom")
def join_room(req: JoinRoomRequest):
    room_id = req.room_id
    room = get_room(room_id)
    if not room.is_open():
        raise HTTPException(status_code=403, detail="Room already full.")
    guest_player_id = req.player_id
    get_player(guest_player_id)
    if room.set_guest_player_id(guest_player_id):
        return {"response": f"Player id {guest_player_id} joined room {room_id} successfully."}
    raise HTTPException(status_code=403, detail=f"Player id {guest_player_id} cannot join room {room_id}")


def kill_old_rooms():
    old_rooms = []
    for rid, room in rooms.items():
        if room.last_ping + 15 < time():
            old_rooms.append(rid)
    for rid in old_rooms:
        del rooms[rid]


@app.get("/listOpenRooms")
def list_open_rooms():
    kill_old_rooms()

    return {"response": {"openRooms": [room.serialize() for room in rooms.values() if room.is_open()]}}


@app.get("/listFullRooms")
def list_full_rooms():
    kill_old_rooms()

    return {"response": {"openRooms": [room.serialize() for room in rooms.values() if len(room.get_guest_player_id()) > 0]}}    # Return if guest is set


@app.put("/sendMessage")
def send_message(req: MessageRequest):

    room_id = req.room_id
    room = get_room(room_id)
    player_id = req.player_id
    get_player(player_id)
    message = req.message
    if room.publish_message(player_id=player_id, message=message):
        return {"response": "Message sent."}
    raise HTTPException(status_code=403, detail=f"Player id {player_id} does not belong in room {room_id}!")


@app.get("/roomState")
def get_room_state(room_id: str):
    room = get_room(room_id)
    room.ping_room()
    return {"response": room.serialize()}


@app.post("/makeMove")
def make_move(req: MakeMoveRequest):
    room_id = req.room_id
    room = get_room(room_id)
    if room.is_open():
        raise HTTPException(status_code=403, detail=f"Cannot make a move while room {room_id} is open.")

    player_id = req.player_id
    get_player(player_id)

    row = req.row
    column = req.column
    puck = req.puck

    board_state: BoardState = room.get_board()
    board_state.make_move(player_id=player_id, row=row, column=column, puck=puck)
    return {"response": room.serialize()}
