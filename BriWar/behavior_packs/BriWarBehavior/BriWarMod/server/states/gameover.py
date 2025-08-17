# coding=utf-8
from ..utils import *
from ..StateBase import BaseState, StateMode


class GameOverState(BaseState):
    state_name = StateMode.gameover  # 设置状态名称

    def __init__(self, namespace, name):
        super(GameOverState, self).__init__(namespace, name)

    def on_enable(self, team):
        Game.AddTimer(10, self.on_gameover)
        if team == "RED":
            CommandComp.SetCommand("title @a title §c红队胜利！")
            Game.SetNotifyMsg("§c红队胜利！")
        elif team == "BLUE":
            CommandComp.SetCommand("title @a title §b蓝队胜利！")
            Game.SetNotifyMsg("§b蓝队胜利！")

    @Listen()
    def ServerPlayerTryDestroyBlockEvent(self, args):
        args["cancel"] = True

    @Listen()
    def PlayerAttackEntityEvent(self, args):
        args["cancel"] = True

    @Listen()
    def ServerEntityTryPlaceBlockEvent(self, args):
        args["cancel"] = True

    def on_gameover(self):
        self.system.fsm.update_state(StateMode.waiting)