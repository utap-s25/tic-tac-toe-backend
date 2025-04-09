import json


class BoardState:

    def __init__(self, host_user_id: str, guest_user_id: str):
        self.board = [["", "", ""], ["", "", ""], ["", "", ""]]
        self.pucks_remaining = {
            str(host_user_id): [1, 2, 3, 4, 5, 6],
            str(guest_user_id): [1, 2, 3, 4, 5, 6]
        }
        self.turn = host_user_id
        """
        Empty string means game is ongoing
        Tie means game is over and tied
        Otherwise, it will be the user_id of the winning player
        """
        self.game_over = ""

    def __str__(self):
        return json.dumps({
            "board": self.board,
            "pucks_remaining": self.pucks_remaining,
            "turn": self.turn,
            "game_over": self.game_over
        })