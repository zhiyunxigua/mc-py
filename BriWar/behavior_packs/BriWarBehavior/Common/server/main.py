# -*- coding: utf-8 -*-
"""
Created on 2025-08-15
服务端系统
"""
from utils import *
from module.Hud import HudModule
from module.Team import TeamModule
from module.Form import FormModule
from module.Knockback import KnockbackModule


class Main(BaseServer):
    def __init__(self, namespace, systemName):
        super(Main, self).__init__(namespace, systemName)
        self.HudModule = None
        self.TeamModule = None
        self.FormModule = None
        self.KnockbackModule = None

    @Listen(priority=0)
    def LoadServerAddonScriptsAfter(self, args):
        self.register_module()

    def register_module(self):
        self.HudModule = HudModule()
        self.TeamModule = TeamModule()
        self.FormModule = FormModule()
        self.KnockbackModule = KnockbackModule()

    @Listen()
    def ClientLoadAddonsFinishServerEvent(self, args):
        """
        客户端加载插件完成
        """
        CF.CreateChatExtension(args["playerId"]).Disable()

    @Listen(event_type=Listen.client)
    def CPS_high(self, args):
        pid = args["__id__"]
        L = args["L"]
        R = args["R"]
        name = NameComp(pid).GetName()
        CommandComp.SetCommand("kick {name} CPS超过阈值，左:{L}，右:{R}".format(name=name, L=L, R=R))


    # API

    # Form Module
    def GetFormBuilder(self, title='未命名表单', _id=str(uuid.uuid4())):
        """
        获取表单构建器
        """
        return self.FormModule.GetFormBuilder(title, _id)



    # Hud Module
    def SetScoreboard(self, args, pid=None):
        """
        设置记分板
        """
        return self.HudModule.SetScoreboard(args, pid)

    def SetPlayerInfoVisible(self, visible, pid=None):
        """
        设置玩家信息可见性
        """
        return self.HudModule.SetPlayerInfoVisible(visible, pid)

    def SetScoreboardTitle(self, title, pid=None):
        """
        设置记分板标题
        """
        return self.HudModule.SetScoreboardTitle(title, pid)

    def SetScoreboardText(self, ID, value, pid=None):
        """
        设置记分板值
        """
        return self.HudModule.SetScoreboardText(ID, value, pid)



    # Team Module
    def CreateTeam(self, teamId, teamName, teamColor, teamHexColor):
        """
        创建队伍
        """
        return self.TeamModule.CreateTeam(teamId, teamName, teamColor, teamHexColor)

    def JoinTeam(self, PlayerId, TeamId):
        """
        加入队伍
        """
        return self.TeamModule.JoinTeam(PlayerId, TeamId)

    def GetAllTeamPlayerList(self):
        """
        获取所有队伍的玩家列表
        """
        return self.TeamModule.GetAllTeamPlayerList()

    def GetTeamListByPlayer(self, PlayerId):
        """
        获取玩家所属的队伍集合
        """
        return self.TeamModule.GetTeamListByPlayer(PlayerId)

    def GetTeamIdByPlayer(self, PlayerId):
        """
        获取玩家所属的队伍id
        """
        return self.TeamModule.GetTeamIdByPlayer(PlayerId)

    def GetNameByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍名称
        """
        return self.TeamModule.GetNameByPlayer(PlayerId)

    def GetColorByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍颜色
        """
        return self.TeamModule.GetColorByPlayer(PlayerId)

    def GetHexColorByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍颜色的十六进制表示
        """
        return self.TeamModule.GetHexColorByPlayer(PlayerId)

    def GetNameByTeam(self, TeamId):
        """
        根据队伍id获取队伍名称
        """
        return self.TeamModule.GetNameByTeam(TeamId)

    def GetColorByTeam(self, TeamId):
        """
        根据队伍id获取队伍颜色
        """
        return self.TeamModule.GetColorByTeam(TeamId)

    def GetHexColorByTeam(self, TeamId):
        """
        根据队伍id获取队伍颜色的十六进制表示
        """
        return self.TeamModule.GetHexColorByTeam(TeamId)

    def GetTeamListById(self, TeamId):
        """
        根据队伍id获取队伍玩家集合
        """
        return self.TeamModule.GetTeamListById(TeamId)

    def RemovePlayerFromTeam(self, PlayerId):
        """
        移除玩家的队伍信息
        """
        return self.TeamModule.RemovePlayerFromTeam(PlayerId)

    def ResetTeam(self):
        """
        重置所有队伍信息
        """
        return self.TeamModule.ResetTeam()

    def ResetOneTeam(self, TeamId):
        """
        重置指定队伍信息
        """
        return self.TeamModule.ResetOneTeam(TeamId)

    def RemoveTeam(self, TeamId):
        """
        移除队伍
        """
        return self.TeamModule.RemoveTeam(TeamId)

