from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4, UUID
from typing import Dict, List, Optional, Tuple

from GameRoom import GameRoom
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


# --- Game State ---


# --- In-Memory Data ---

players: list[Player] = []
rooms: Dict[str, GameRoom] = {}


def get_room(room_id: str) -> GameRoom:
    room = rooms.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found!")
    return room


def get_player(player_id: str) -> Player:
    for player in players:
        if player.player_id == player_id:
            return player
    raise HTTPException(status_code=404, detail=f"Player {player_id} not found!")


# --- API Endpoints ---

@app.put("/createPlayer")
def create_player(req: CreatePlayerRequest):
    player_name = req.player_name
    for existing_player in players:
        if existing_player.player_name == player_name:
            raise HTTPException(status_code=400,
                                detail=f'A player {existing_player.player_id} with the given name "{player_name}" '
                                       f'already exists!')
    random_id = str(uuid4())
    new_player = Player(player_id=random_id, player_name=player_name)
    players.append(new_player)
    print(f"Created new player: {new_player}")
    return {
        "response": {
            "player_id": random_id
        }
    }


@app.put("/createRoom")
def create_room(req: CreateRoomRequest):
    player_id = req.player_id
    found = False
    for existing_player in players:
        if existing_player.player_id == player_id:
            found = True
            break
    if not found:
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
    if room.set_guest_player_id(guest_player_id):
        return {"response": f"Player id {guest_player_id} joined room {room_id} successfully."}
    raise HTTPException(status_code=403, detail=f"Player id {guest_player_id} cannot join room {room_id}")


@app.get("/listOpenRooms")
def list_open_rooms():
    return {"response": {"openRooms": [str(rid) for rid, room in rooms.items() if room.is_open()]}}


@app.put("/sendMessage")
def send_message(req: MessageRequest):
    room_id = req.room_id
    room = get_room(room_id)
    player_id = req.player_id
    message = req.message
    if room.publish_message(player_id=player_id, message=message):
        return {"response": "Message sent."}
    raise HTTPException(status_code=403, detail=f"Player id {player_id} does not belong in room {room_id}!")


@app.get("/fetchMessages")
def fetch_messages(room_id: str):
    room = get_room(room_id)
    messages: list[tuple[str, str]] = room.get_messages()
    friendly_messages = []
    for player_id, message in messages:
        player = get_player(player_id)
        friendly_messages.append([player.player_name, message])
    return {"response": {"messages": friendly_messages}}
