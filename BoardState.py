import json

STILL_PLAYING = ""
TIE = "TIE"


class BoardState:

    def __init__(self, host_player_id: str, guest_player_id: str):
        # [player_id or empty_string, puck_size]
        self.board = [
            [["", "0"], ["", "0"], ["", "0"]],
            [["", "0"], ["", "0"], ["", "0"]],
            [["", "0"], ["", "0"], ["", "0"]]
        ]
        self.host_player_id = host_player_id
        self.guest_player_id = guest_player_id
        self.pucks_remaining = {
            str(host_player_id): [1, 2, 3, 4, 5, 6],
            str(guest_player_id): [1, 2, 3, 4, 5, 6]
        }
        self.turn = host_player_id
        """
        Empty string means game is ongoing
        Tie means game is over and tied
        Otherwise, it will be the user_id of the winning player
        """
        self.game_over = STILL_PLAYING

    def get_current_player(self):
        return self.turn

    def get_waiting_player(self):
        for player in self.pucks_remaining.keys():
            if player != self.turn:
                return player
        return None

    def __str__(self):
        return json.dumps({
            "board": self.board,
            "pucks_remaining": self.pucks_remaining,
            "turn": self.turn,
            "game_over": self.game_over
        })
