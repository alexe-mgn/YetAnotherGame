from Engine.character import BasePlayer, BaseEnemy
from game_class import YTGBaseCreature


class YTGBasePlayer(BasePlayer, YTGBaseCreature):
    pass


class YTGBaseEnemy(BaseEnemy, YTGBaseCreature):
    pass
