# coding=utf-8
"""
Created on 2024/10/1
HudUi模块
这里主要 控制游戏的hud界面
接口：
- SetPlayerInfoVisible(visible)                设置玩家信息可见性
- SetScoreboard(scoreboard, pid)               设置记分板
- SetScoreboardTitle(title, pid)               设置记分板标题
- SetScoreboardText(id, value, pid)            设置记分板值
"""
from ..utils import *

class HudModule(BaseModule):
    def __init__(self):
        super(HudModule, self).__init__()
        Game.AddRepeatedTimer(5, self.ping_timer)
        self.anchor_bar = False

    def SetPlayerInfoVisible(self, visible, pid):
        """
        设置玩家信息可见性
        """
        self.NotifyToClient(pid, 'SetPlayerInfoVisible', visible)

    def SetScoreboard(self, scoreboard, pid=None):
        """
        设置记分板
        """
        self.NotifyToClient(pid, 'SetScoreboard', scoreboard)

    def SetScoreboardTitle(self, title, pid=None):
        """
        设置记分板标题
        """
        self.NotifyToClient(pid, 'SetScoreboardTitle', title)

    def SetScoreboardText(self, ID, value, pid=None):
        """
        设置记分板值
        """
        self.NotifyToClient(pid, 'SetScoreboardText', {"name": ID, "text": value})

    def ping_timer(self):
        self.NotifyToMultiClients(serverApi.GetPlayerList(), "ping_value", time.time() * 1000)

    @Listen()
    def OnScriptTickServer(self):
        if self.anchor_bar:
            players_pos = {pid: PosComp(pid).GetPos() for pid in serverApi.GetPlayerList()}
            eventData = {"players_pos": players_pos, "team_data": self.system.TeamController.GetAllTeamPlayerList()}
            self.NotifyToMultiClients(serverApi.GetPlayerList(), "players_pos", eventData)
