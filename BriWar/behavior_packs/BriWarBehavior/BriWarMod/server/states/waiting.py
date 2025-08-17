# coding=utf-8
from ..utils import *
from ..StateBase import BaseState, StateMode
hud_str_dict = {
    "title": "战桥",
    "order": ("1", "2", "3", "4", "5"),
    "text_dict": {
        "1": "",
        "2": "等待中...",
        "3": "",
        "4": "当前人数: ",
        "5": "",
    }
}

class WaitingState(BaseState):
    """等待状态，游戏开始前的等待阶段"""

    state_name = StateMode.waiting  # 设置状态名称

    def __init__(self, namespace, name):
        """初始化等待状态"""
        super(WaitingState, self).__init__(namespace, name)
        # 添加倒计时子状态
        self.countdown_state = self.add_sub_state(CountdownState)
        self.player_list = set()

    def on_enable(self, *args, **kwargs):
        """等待状态启用时的逻辑"""
        for pid in serverApi.GetPlayerList():
            self.OnLocalPlayerStopLoading({"__id__": pid})

    @Listen(event_type=Listen.client)
    def OnLocalPlayerStopLoading(self, args):
        pid = args["__id__"]
        CommandComp.SetCommand("clear @s", pid)
        PosComp(pid).SetPos(SPAWN_POS)
        RotComp(pid).SetRot(SPAWN_ROT)
        self.player_list.add(pid)
        CF.CreatePlayer(pid).SetPlayerGameType(minecraftEnum.GameType.Survival)
        common = self.system.Common
        common.SetScoreboard(hud_str_dict, pid)
        common.SetScoreboardText("2", "等待中...")
        common.SetScoreboardText("4", "当前人数: §e{}".format(len(self.player_list)))
        if len(self.player_list) == 2:
            Game.SetNotifyMsg("§a人数足够，开始倒计时")
            self.start_counting()

    @Listen()
    def ServerEntityTryPlaceBlockEvent(self, args):
        args["cancel"] = True

    @Listen()
    def ServerPlayerTryDestroyBlockEvent(self, args):
        args["cancel"] = True

    @Listen()
    def PlayerAttackEntityEvent(self, args):
        args["cancel"] = True

    @Listen()
    def HealthChangeBeforeServerEvent(self, args):
        args["cancel"] = True
        pid = args["entityId"]
        entityFootPos = PosComp(pid).GetFootPos()
        if entityFootPos[1] <= -60:
            CF.CreateDimension(pid).ChangePlayerDimension(0, SPAWN_POS)
            RotComp(pid).SetRot(SPAWN_ROT)

    @Listen()
    def PlayerJoinMessageEvent(self, args):
        name = args["name"]
        args["message"] = JOIN_MESSAGE.format(name=name)

    @Listen()
    def PlayerLeftMessageServerEvent(self, args):
        name = args["name"]
        args["message"] = LEFT_MESSAGE.format(name=name)
        self.player_list.remove(args["id"])
        common = self.system.Common
        common.SetScoreboardText("4", "当前人数: §e{}".format(len(self.player_list)))
        if len(self.player_list) == 1:
            self.countdown_state._on_disable()
            Game.SetNotifyMsg("§c人数不足，停止倒计时")
            common = self.system.Common
            common.SetScoreboardText("2", "等待中...")

    def start_counting(self):
        """开始倒计时（激活倒计时子状态）"""
        self.start_sub_state("countdown")

    def on_disable(self):
        """等待状态禁用时的逻辑"""
        # 父类会自动处理子状态的禁用，这里不需要额外操作
        self.player_list.clear()


# 倒计时子状态实现
class CountdownState(BaseState):
    """倒计时子状态，处理游戏开始前的倒计时逻辑"""

    state_name = "countdown"  # 设置状态名称

    def __init__(self, namespace, name):
        """初始化倒计时状态"""
        super(CountdownState, self).__init__(namespace, name)
        self.time = 0
        self.timer = None

    def on_enable(self):
        """倒计时状态启用时的逻辑"""
        logger.info("Countdown started")
        self.time = COUNTDOWN_TIME + 0
        self.timer = Game.AddRepeatedTimer(1, self.countdown)

    def countdown(self):
        self.time -= 1
        CommandComp.SetCommand("title @a title §a")
        CommandComp.SetCommand("title @a subtitle §a{time}".format(time=self.time))
        common = self.system.Common
        common.SetScoreboardText("2", "倒计时: §e{}§f秒".format(self.time))
        if self.time <= 0:
            self.system.fsm.update_state(StateMode.gaming)

    def on_disable(self):
        """倒计时状态禁用时的逻辑"""
        logger.info("Countdown stopped")
        Game.CancelTimer(self.timer)
