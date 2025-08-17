# coding=utf-8
"""
Created on 2025/6/27
队伍模块
这里主要控制游戏的队伍，管理队伍创建、加入、查询和移除，基于内存存储，通过计分板 Team 跟踪玩家队伍，支持随机分配未选择小队的玩家（包括有 party 玩家因满员未分配的情况）。
前置条件：
- 已创建名为"Team"的计分板
接口：
- CreateTeam(TeamId, TeamName, TeamColor, TeamHexColor) 创建队伍
- JoinTeam(PlayerId, TeamId)                            加入队伍
- GetAllTeamPlayerList()                                获取所有队伍的玩家列表
- GetTeamListByPlayer(PlayerId)                         获取玩家所属的队伍集合
- GetTeamIdByPlayer(PlayerId)                           获取玩家所属的队伍id
- GetNameByPlayer(PlayerId)                             根据玩家id获取队伍名称
- GetColorByPlayer(PlayerId)                            根据玩家id获取队伍颜色
- GetHexColorByPlayer(PlayerId)                         根据玩家id获取队伍颜色的十六进制表示
- GetNameByTeam(TeamId)                                 根据队伍id获取队伍名称
- GetColorByTeam(TeamId)                                根据队伍id获取队伍颜色
- GetHexColorByTeam(TeamId)                             根据队伍id获取队伍颜色的十六进制表示
- GetTeamListById(TeamId)                               根据队伍id获取队伍玩家集合
- RemovePlayerFromTeam(PlayerId)                        移除玩家的队伍信息
- ResetTeam()                                           重置所有队伍信息
- ResetOneTeam(TeamId)                                  重置指定队伍信息
- RemoveTeam(TeamId)                                    移除队伍
- RandomAllocateTeams()                                 随机分配未选择小队的玩家到队伍
"""
from ..utils import *
import mod.server.extraServerApi as serverApi
import random
import weakref

class TeamIdEnums:
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    PINK = "PINK"
    CYAN = "CYAN"
    PURPLE = "PURPLE"
    ORANGE = "ORANGE"
    WHITE = "WHITE"
    BLACK = "BLACK"

class TeamModule(BaseModule):
    def __init__(self):
        super(TeamModule, self).__init__()
        self.teamDict = {}

    def CreateTeam(self, TeamId, TeamName, TeamColor, TeamHexColor):
        """
        创建队伍
        :param TeamId: 队伍id
        :param TeamName: 队伍名称
        :param TeamColor: 队伍颜色
        :param TeamHexColor: 队伍颜色的十六进制表示
        :return: 是否创建成功
        """
        if TeamId in self.teamDict:
            return False
        teamInfo = {
            "Id": TeamId,
            "Name": TeamName,
            "Color": TeamColor,
            "HexColor": TeamHexColor,
            "Index": len(self.teamDict) + 1,
        }
        self.teamDict[TeamId] = teamInfo
        return True

    def JoinTeam(self, PlayerId, TeamId):
        """
        加入队伍
        :param PlayerId: 玩家id
        :param TeamId: 队伍id
        :return: 是否加入成功
        """
        Name = NameComp(PlayerId).GetName()
        TeamIndex = 0
        for teamId, teamInfo in self.teamDict.items():
            if teamId == TeamId:
                TeamIndex = teamInfo["Index"]
                break
        return CommandComp().SetCommand("/scoreboard players set %s Team %d" % (Name, TeamIndex))

    def GetAllTeamPlayerList(self):
        """
        获取所有队伍的玩家列表
        :return: 所有队伍的玩家列表
        """
        teamDict = {}
        for team in self.teamDict.keys():
            teamDict[team] = [pid for pid in serverApi.GetPlayerList() if self.GetTeamIdByPlayer(pid) == team]
        return teamDict  # type: dict[TeamId, list(PlayerId)]

    def GetTeamListByPlayer(self, PlayerId):
        """
        获取玩家所属的队伍集合
        :return: 队伍列表
        """
        self.CreateTeam("RED", "红队", "§c", "#FF0000")
        team = self.GetTeamIdByPlayer(PlayerId)
        if team is None:
            return set()
        return self.GetTeamListById(team)

    def GetTeamIdByPlayer(self, PlayerId):
        """
        获取玩家所属的队伍id
        :return: 队伍id
        """
        scoreList = []
        for ScoreboardObject in Game().GetAllPlayerScoreboardObjects():
            if ScoreboardObject["playerId"] == PlayerId:
                scoreList = ScoreboardObject["scoreList"]
                break
        Team = None
        for score in scoreList:
            if score["name"] == "Team":
                for teamId, teamInfo in self.teamDict.items():
                    if teamInfo["Index"] == score["value"]:
                        Team = teamInfo["Id"]
                break
        return Team

    def GetNameByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍名称
        :param PlayerId: 玩家id
        :return: 队伍名称
        """
        team = self.GetTeamIdByPlayer(PlayerId)
        return self.GetNameByTeam(team)

    def GetColorByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍颜色
        :param PlayerId: 玩家id
        :return: 队伍颜色
        """
        team = self.GetTeamIdByPlayer(PlayerId)
        return self.GetColorByTeam(team)

    def GetHexColorByPlayer(self, PlayerId):
        """
        根据玩家id获取队伍颜色的十六进制表示
        :param PlayerId: 玩家id
        :return: 队伍颜色的十六进制表示
        """
        team = self.GetTeamIdByPlayer(PlayerId)
        return self.GetHexColorByTeam(team)

    def GetNameByTeam(self, TeamId):
        """
        根据队伍id获取队伍名称
        :param TeamId: 队伍id
        :return: 队伍名称
        """
        teamInfo = self.GetTeamInfoById(TeamId)
        if teamInfo is None:
            return None
        return teamInfo["Name"]

    def GetColorByTeam(self, TeamId):
        """
        根据队伍id获取队伍颜色
        :param TeamId: 队伍id
        :return: 队伍颜色
        """
        teamInfo = self.GetTeamInfoById(TeamId)
        if teamInfo is None:
            return None
        return teamInfo["Color"]

    def GetHexColorByTeam(self, TeamId):
        """
        根据队伍id获取队伍颜色的十六进制表示
        :param TeamId: 队伍id
        :return: 队伍颜色的十六进制表示
        """
        teamInfo = self.GetTeamInfoById(TeamId)
        if teamInfo is None:
            return None
        return teamInfo["HexColor"]

    def GetTeamListById(self, TeamId):
        """
        根据队伍id获取队伍玩家集合
        :param TeamId: 队伍id
        :return: 队伍玩家集合
        """
        TeamList = set()
        for pid in serverApi.GetPlayerList():
            team = self.GetTeamIdByPlayer(pid)
            if team == TeamId:
                TeamList.add(pid)
        return TeamList  # type: set(PlayerId)

    def GetTeamInfoById(self, TeamId):
        """
        根据队伍id获取队伍信息
        """
        for teamId, teamInfo in self.teamDict.items():
            if teamId == TeamId:
                return teamInfo
        return None

    def RemovePlayerFromTeam(self, PlayerId):
        """
        移除玩家的队伍信息
        :param PlayerId: 玩家id
        :return: 是否移除成功
        """
        Name = NameComp(PlayerId).GetName()
        return CommandComp().SetCommand("/scoreboard players set %s Team 0" % Name)

    def ResetTeam(self):
        """
        重置所有队伍信息
        :return: 是否重置成功
        """
        return CommandComp().SetCommand("/scoreboard players set @a Team 0")

    def ResetOneTeam(self, TeamId):
        """
        重置指定队伍信息
        :param TeamId: 队伍id
        :return: 是否重置成功
        """
        for pid in serverApi.GetPlayerList():
            team = self.GetTeamIdByPlayer(pid)
            if team == TeamId:
                Name = NameComp(pid).GetName()
                success = CommandComp().SetCommand("/scoreboard players set %s Team 0" % Name)
                if not success:
                    return False
        return True

    def RemoveTeam(self, TeamId):
        """
        移除队伍
        :param TeamId: 队伍id
        :return: 是否移除成功
        """
        if TeamId in self.teamDict:
            del self.teamDict[TeamId]
            return True
        return False
