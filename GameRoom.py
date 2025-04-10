from uuid import uuid4, UUID
from BoardState import BoardState


class GameRoom:

    def __init__(self, host_player_id: str):
        self.room_id = uuid4()
        self.host_player_id = host_player_id
        self.guest_player_id = ""
        self.board_state: BoardState | None = None
        self.messages: list[tuple[str, str]] = []  # (userid, message)

    def get_room_id(self) -> UUID:
        return self.room_id

    def is_open(self) -> bool:
        return len(self.guest_player_id) == 0

    def get_host_player_id(self):
        return self.host_player_id

    def get_guest_player_id(self):
        return self.guest_player_id

    def set_guest_player_id(self, guest_player_id: str) -> bool:
        if len(self.guest_player_id) == 0:
            self.guest_player_id = guest_player_id
            self.board_state = BoardState(self.host_player_id, guest_player_id)
            return True
        return False

    def get_messages(self):
        return self.messages

    def publish_message(self, player_id: str, message: str) -> bool:
        if player_id in [self.host_player_id, self.guest_player_id]:
            self.messages.append((player_id, message))
            return True
        return False

    def update_board(self, proposed_board_state: BoardState) -> bool:
        # Ensure that the next proposed_board_state
        # can be reached by making a move from the current state
        self.board_state = proposed_board_state
        return True

    def get_board(self) -> BoardState:
        return self.board_state
