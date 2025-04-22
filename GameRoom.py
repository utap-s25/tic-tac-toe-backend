from uuid import uuid4, UUID
from BoardState import BoardState
from pydantic import BaseModel
from time import time

from UniqueWordGenerator import UniqueWordGenerator


class Message(BaseModel):
    id_or_name: str
    message: str


word_generator = UniqueWordGenerator()


class GameRoom:

    def __init__(self, host_player_id: str):
        self.room_id = word_generator.generate(8)
        self.host_player_id = host_player_id
        self.guest_player_id = ""
        self.board_state = BoardState(self.host_player_id, self.guest_player_id)
        self.messages: list[Message] = []  # (userid, message)
        self.last_ping = time()

    def get_room_id(self) -> UUID:
        return self.room_id

    def is_open(self) -> bool:
        return len(self.guest_player_id) == 0

    def get_host_player_id(self):
        return self.host_player_id

    def get_guest_player_id(self):
        return self.guest_player_id

    def set_guest_player_id(self, guest_player_id: str) -> bool:
        if len(self.guest_player_id) == 0 and self.host_player_id != guest_player_id:
            self.guest_player_id = guest_player_id
            self.board_state = BoardState(self.host_player_id, guest_player_id)
            return True
        return False

    def is_room_full(self):
        return len(self.host_player_id) > 0 and len(self.guest_player_id) > 0

    def get_messages(self):
        return self.messages

    def publish_message(self, player_id: str, message: str) -> bool:
        if player_id in [self.host_player_id, self.guest_player_id]:
            self.messages.append(Message(id_or_name=player_id, message=message))
            return True
        return False

    def update_board(self, proposed_board_state: BoardState) -> bool:
        # Ensure that the next proposed_board_state
        # can be reached by making a move from the current state
        self.board_state = proposed_board_state
        return True

    def ping_room(self):
        self.last_ping = time()

    def get_board(self) -> BoardState:
        return self.board_state
