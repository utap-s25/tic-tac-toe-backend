import json
from uuid import UUID, uuid4


class Player:

    def __init__(self, player_uuid: UUID, user_name: str):
        self.player_uuid = player_uuid
        self.user_name = user_name

    def __str__(self):
        return json.dumps({"player_uuid": str(self.player_uuid), "user_name": self.user_name})


EMPTY_PLAYER = Player(uuid4(), "Bob Dylan")
print(EMPTY_PLAYER)
