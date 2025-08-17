# coding=utf-8
import random

from mod import common

from ..utils import *
from ..StateBase import BaseState, StateMode

hud_str_dict = {
    "title": "战桥",
    "order": ("sep", "round", "time", "RED", "BLUE", "sep1"),
    "text_dict": {
        "sep": "§e------------------",
        "round": "第 §b0 回合",
        "time": "回合剩余时间 §e00:00",
        "RED": "§c红队 §e0§f分",
        "BLUE": "§9蓝队 §e0§f分",
        "sep1": "§e§e------------------"
    }
}


class GamingState(BaseState):
    state_name = StateMode.gaming  # 设置状态名称

    def __init__(self, namespace, name):
        super(GamingState, self).__init__(namespace, name)
        self.RoundState = self.add_sub_state(RoundState)  # 添加子状态
        self.Round = 0  # 当前回合数
        self.team = {}
        self.score = {}

    def on_enable(self, *args, **kwargs):
        Game.SetDefaultGameType(minecraftEnum.GameType.Spectator)
        self.Round = 1
        self.team = {
            "RED": [],
            "BLUE": []
        }
        self.score = {
            "RED": 0,
            "BLUE": 0
        }
        logger.debug("gaming on_enable")
        common = self.system.Common
        common.SetScoreboard(hud_str_dict)
        players = serverApi.GetPlayerList()
        random.shuffle(players)
        CommandComp.SetCommand("title @a title §a游戏开始")
        for i in range(0, len(players), 2):
            pid = players[i]
            self.team["RED"].append(pid)
            CommandComp.SetCommand("title @s subtitle §c红队", pid)
            common.SetScoreboardText("RED", "§c红队 §e0§f分 §7<-我", pid)
            CF.CreatePlayer(pid).SetPlayerRespawnPos(RED_SPAWN_POS)
            if i == len(players) - 1:
                break
            pid = players[i + 1]
            self.team["BLUE"].append(pid)
            CommandComp.SetCommand("title @s subtitle §b蓝队", pid)
            common.SetScoreboardText("BLUE", "§9蓝队 §e0§f分 §7<-我", pid)
            CF.CreatePlayer(pid).SetPlayerRespawnPos(BLUE_SPAWN_POS)
        self.start_sub_state("round")

    def next_round(self, victory_team):
        common = self.system.Common
        if victory_team == "RED":
            self.score["RED"] += 1
            common.SetScoreboardText("RED", "§c红队 §e{}§f分".format(self.score["RED"]))
            Game.SetNotifyMsg("§c红队得分！")
        elif victory_team == "BLUE":
            self.score["BLUE"] += 1
            common.SetScoreboardText("BLUE", "§9蓝队 §e{}§f分".format(self.score["BLUE"]))
            Game.SetNotifyMsg("§b蓝队得分！")
        elif victory_team == "TIME_OUT":
            Game.SetNotifyMsg("时间到，红蓝双方平分！")
        if self.score["RED"] == 10:
            self.system.fsm.update_state(StateMode.gameover, "RED")
            return
        elif self.score["BLUE"] == 10:
            self.system.fsm.update_state(StateMode.gameover, "BLUE")
            return
        self.Round += 1
        self.RoundState._on_enable()

    @Listen()
    def PlayerJoinMessageEvent(self, args):
        args["cancel"] = True

    @Listen()
    def PlayerLeftMessageServerEvent(self, args):
        pid = args["id"]
        if pid in self.team["RED"]:
            self.team["RED"].remove(pid)
            if len(self.team["RED"]) == 0:
                self.system.fsm.update_state(StateMode.gameover, "BLUE")
        elif pid in self.team["BLUE"]:
            self.team["BLUE"].remove(pid)
            if len(self.team["BLUE"]) == 0:
                self.system.fsm.update_state(StateMode.gameover, "RED")

    @Listen(event_type=Listen.client)
    def OnLocalPlayerStopLoading(self, args):
        pid = args["__id__"]
        CommandComp.SetCommand("clear @s", pid)
        CF.CreatePlayer(pid).SetPlayerGameType(minecraftEnum.GameType.Spectator)
        PosComp(pid).SetPos(SPAWN_POS)
        RotComp(pid).SetRot(SPAWN_ROT)

class RoundState(BaseState):
    """回合子状态，处理游戏开始前的倒计时逻辑"""

    state_name = "round"  # 设置状态名称

    def __init__(self, namespace, name):
        """初始化状态"""
        super(RoundState, self).__init__(namespace, name)
        self.timer = None  # 倒计时计时器
        self.time = 0  # 倒计时时间
        self.block_set = set()  # 方块集合

    def on_enable(self):
        self.timer = Game.AddRepeatedTimer(1, self.on_timer)
        self.time = ROUND_TIME + 0
        common = self.system.Common
        common.SetScoreboardText("round", "第 §b{} §f回合！".format(self.parent_state.Round))
        CommandComp.SetCommand("title @a title 第 §b{} §f回合！".format(self.parent_state.Round))
        CommandComp.SetCommand("kill @e[type=!player]")
        CommandComp.SetCommand("clear @a")
        for pid in self.parent_state.team["RED"]:
            ItemComp(pid).SetPlayerAllItems(RED_PLAYER_ITEMS)
            PosComp(pid).SetPos(RED_SPAWN_POS)
            RotComp(pid).SetRot(RED_SPAWN_ROT)
        for pid in self.parent_state.team["BLUE"]:
            ItemComp(pid).SetPlayerAllItems(BLUE_PLAYER_ITEMS)
            PosComp(pid).SetPos(BLUE_SPAWN_POS)
            RotComp(pid).SetRot(BLUE_SPAWN_ROT)

    def on_timer(self):
        common = self.system.Common
        common.SetScoreboardText("time", "回合剩余时间 §e{}".format("%02d" % self.time))
        self.time -= 1
        if self.time <= 0:
            self._on_disable("TIME_OUT")

    @Listen()
    def ServerEntityTryPlaceBlockEvent(self, args):
        """监听玩家尝试放置方块事件"""
        pos = (args['x'], args['y'], args['z'])
        self.block_set.add(pos)

    @Listen()
    def PlayerRespawnFinishServerEvent(self, args):
        """监听玩家尝试放置方块事件"""
        pid = args["playerId"]
        if pid in self.parent_state.team["RED"]:
            CommandComp.SetCommand("clear @s", pid)
            ItemComp(pid).SetPlayerAllItems(RED_PLAYER_ITEMS)
        if pid in self.parent_state.team["BLUE"]:
            CommandComp.SetCommand("clear @s", pid)
            ItemComp(pid).SetPlayerAllItems(BLUE_PLAYER_ITEMS)

    @Listen("ServerPlayerTryDestroyBlockEvent")
    def ServerPlayerTryDestroyBlock(self, args):
        """监听玩家尝试破坏方块事件"""
        fullName = args["fullName"]
        pos = (args['x'], args['y'], args['z'])
        args["cancel"] = True
        if fullName == "minecraft:bed":
            bed_color = BlockComp.GetBedColor(pos, 0)
            if bed_color == 1:
                self._on_disable("BLUE")
            elif bed_color == 4:
                self._on_disable("RED")
        elif pos in self.block_set:
            self.block_set.remove(pos)
            args["cancel"] = False

    def on_disable(self, *args):
        Game.CancelTimer(self.timer)
        for pos in self.block_set:
            CommandComp.SetCommand("setblock %d %d %d air" % pos)
        self.block_set.clear()
        if len(args) >= 1:
            Game.AddTimer(0.01, lambda: self.parent_state.next_round(args[0]))


