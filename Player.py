import json
from uuid import UUID, uuid4


class Player:

    def __init__(self, player_id: str, player_name: str):
        self.player_id = player_id
        self.player_name = player_name

    def __str__(self):
        return json.dumps({"player_id": self.player_id, "player_name": self.player_name})


EMPTY_PLAYER = Player(str(uuid4()), "Bob Dylan")
print(EMPTY_PLAYER)
