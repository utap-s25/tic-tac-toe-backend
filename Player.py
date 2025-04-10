import json
from uuid import UUID, uuid4


class Player:

    def __init__(self, player_uuid: str, player_name: str):
        self.player_uuid = player_uuid
        self.player_name = player_name

    def __str__(self):
        return json.dumps({"player_uuid": self.player_uuid, "player_name": self.player_name})


EMPTY_PLAYER = Player(str(uuid4()), "Bob Dylan")
print(EMPTY_PLAYER)
