import json

from fastapi import HTTPException

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

    def make_move(self, player_id: str, row: int, column: int, puck: int):
        game_status = self.check_game_over()
        if game_status != STILL_PLAYING:
            raise HTTPException(status_code=400, detail=f"The game is already over, result: ${game_status}")

        # Only the host and guest player's may make a move here
        if player_id not in [self.host_player_id, self.guest_player_id]:
            raise HTTPException(status_code=400, detail=f"Player id {player_id} does not belong in this board!")
        # Only the current player can make a move
        if player_id != self.turn:
            raise HTTPException(status_code=400, detail=f"Player id {player_id} cannot move, it is ${self.turn} turn!")

        # current player has no pucks left!
        player_pucks = self.pucks_remaining.get(player_id, [])
        if len(player_pucks) == 0:
            raise HTTPException(status_code=400, detail=f"Player id {player_id} has no pucks left!")
        # current player using a puck that does not exist
        if puck not in player_pucks:
            raise HTTPException(status_code=400,
                                detail=f"Player id {player_id} puck ${puck} not found in ${player_pucks}!")

        tile = self.board[row][column]
        tile_owner = tile[0]
        tile_puck_size = int(tile[1])

        if tile_owner == "" or tile_puck_size < puck:
            # Place the player puck
            tile[0] = player_id
            tile[1] = str(puck)
            # Remove the puck from the list of player's pucks
            player_pucks.remove(puck)
        else:
            raise HTTPException(status_code=400,
                                detail=f"Player id {player_id} cannot place puck ${puck} at (${row},${column})!")

        # The move was valid and successful
        # Alternate the turns
        if self.turn == self.host_player_id:
            self.turn = self.guest_player_id
        else:
            self.turn = self.host_player_id

        # It is now the other's player's turn, check game over
        updated_game_status = self.check_game_over()
        self.game_over = updated_game_status


    def __str__(self):
        return json.dumps({
            "board": self.board,
            "pucks_remaining": self.pucks_remaining,
            "turn": self.turn,
            "game_over": self.game_over
        })

    """ 
    Return an empty string if the game is still not over.
    Return the playerId of the player who won based on the current board 
    (3 of their pucks in a row, horizontal, vertical, or diagonal)
    Return "TIE" if no more moves can be made by the current player to move (denoted by "turn")
    """

    def check_game_over(self):
        def get_owner(row: int, column: int):
            return self.board[row][column][0]

        # 8 possible win lines (3 rows, 3 cols, 2 diagonals)
        lines = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            p1, p2, p3 = line
            o1 = get_owner(*p1)
            o2 = get_owner(*p2)
            o3 = get_owner(*p3)
            if o1 != "" and o1 == o2 == o3:
                self.game_over = o1
                return o1

        # Check if current player has any remaining moves
        current_player = self.turn
        pucks = self.pucks_remaining.get(current_player, [])
        if len(pucks) == 0:
            self.game_over = TIE
            return TIE

        can_move = False
        for size in pucks:
            for r in range(3):
                for c in range(3):
                    tile = self.board[r][c]
                    tile_owner = tile[0]
                    tile_puck_size = int(tile[1])
                    if tile_owner == "" or tile_puck_size < size:
                        can_move = True
                        break
                if can_move:
                    break

        if not can_move:
            self.game_over = TIE
            return TIE

        return STILL_PLAYING


"""
Return a list BoardState objects that represent all possible next board_states
"""


def get_next_board_states(current: BoardState):
    if current.game_over != STILL_PLAYING:
        return []

    current_player = current.get_current_player()
    pucks = current.pucks_remaining[current_player]
    next_states = []

    for size in pucks:
        for r in range(3):
            for c in range(3):
                tile = current.board[r][c]
                tile_owner = tile[0]
                tile_puck_size = int(tile[1])
                if tile_owner == "" or tile_puck_size < size:
                    # Copy current state into new one
                    next_state = BoardState(current.host_player_id, current.guest_player_id)
                    next_state.board = [row.copy() for row in current.board]
                    next_state.pucks_remaining = {
                        player: values.copy() for player, values in current.pucks_remaining.items()
                    }
                    next_state.turn = current.get_waiting_player()

                    # Place puck
                    next_state.board[r][c] = [current_player, str(size)]
                    next_state.pucks_remaining[current_player].remove(size)

                    # Check if this move ends the game
                    next_state.check_game_over()

                    next_states.append(next_state)

    return next_states


board_state = BoardState("a", "b")
board_state_string = str(board_state)
board_state_json = json.loads(board_state_string)
print(json.dumps(board_state_json, indent=2))
