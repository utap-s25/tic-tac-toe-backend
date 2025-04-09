from uuid import uuid4, UUID
from BoardState import BoardState


class GameRoom:

    def __init__(self, host_user_id: str):
        self.room_id = uuid4()
        self.host_user_id = host_user_id
        self.guest_user_id = ""
        self.board_state = BoardState(host_user_id, "")
        self.messages: list[tuple[str, str]] = []  # (userid, message)

    def get_room_id(self) -> UUID:
        return self.room_id

    def is_open(self) -> bool:
        return len(self.guest_user_id) == 0

    def get_host_user_id(self):
        return self.host_user_id

    def get_guest_user_id(self):
        return self.guest_user_id

    def set_guest_user_id(self, guest_user_id: str) -> bool:
        if len(self.guest_user_id) == 0:
            self.guest_user_id = guest_user_id
            return True
        return False

    def get_messages(self):
        return self.messages

    def publish_message(self, user_id: str, message: str) -> bool:
        if user_id in [self.host_user_id, self.guest_user_id]:
            self.messages.append((user_id, message))
            return True
        return False

    def update_board(self, proposed_board_state: BoardState) -> bool:
        # Ensure that the next proposed_board_state
        # can be reached by making a move from the current state
        self.board_state = proposed_board_state
        return True

    def get_board(self) -> BoardState:
        return self.board_state
