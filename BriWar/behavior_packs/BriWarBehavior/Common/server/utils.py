# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi, mod.common.minecraftEnum as minecraftEnum
import random, time, weakref, uuid, json
from mod_log import logger as logger
from .config import *
ServerSystem = serverApi.GetServerSystemCls()
CF = serverApi.GetEngineCompFactory()
LevelId = serverApi.GetLevelId()
Game = CF.CreateGame(LevelId)
PlayerComp = CF.CreatePlayer(LevelId)
CommandComp = CF.CreateCommand(LevelId)
BlockComp = CF.CreateBlockInfo(LevelId)
ChestBlockComp = CF.CreateChestBlock(LevelId)

def PosComp(PlayerId):
    return CF.CreatePos(PlayerId)

def RotComp(PlayerId):
    return CF.CreateRot(PlayerId)

def ItemComp(PlayerId):
    return CF.CreateItem(PlayerId)

def NameComp(PlayerId):
    return CF.CreateName(PlayerId)

def DataComp(PlayerId):
    return CF.CreateExtraData(PlayerId)

def MsgComp(PlayerId):
    return CF.CreateMsg(PlayerId)

class Listen(object):
    Minecraft = "Minecraft"
    server = "server"
    client = "client"
    def __init__(self, event_name=None, event_type='Minecraft', priority=3):
        self.event_name = event_name
        self.event_type = event_type
        self.priority = priority

    def __call__(self, func):
        func.listen_type = self.event_type
        func.listen_event = self.event_name or func.__name__
        func.listen_priority = self.priority
        return func

class BaseServer(ServerSystem):
    ListenDict = {"Minecraft": ("Minecraft", "Engine"), "client": (modName, "main"), "server": (modName, "main")}
    def __init__(self, namespace, systemName):
        super(BaseServer, self).__init__(namespace, systemName)
        self.Register()

    def Register(self):
        for key in dir(self):
            obj = getattr(self, key)
            if callable(obj) and hasattr(obj, 'listen_event'):
                event = getattr(obj, 'listen_event')
                _type = getattr(obj, 'listen_type')
                priority = getattr(obj, 'listen_priority')
                self.listen(event, obj, _type=_type, priority=priority)

    def listen(self, event, func, _type, priority):
        if _type not in self.ListenDict:
            name, system = _type, "main"
        else:
            name, system = self.ListenDict[_type]
        self.ListenForEvent(name, system, event, self, func, priority=priority)


class BaseModule(object):
    ListenDict = {"Minecraft": ("Minecraft", "Engine"), "client": (modName, "main"), "server": (modName, "main")}
    system = None
    def __init__(self):
        self.system = weakref.proxy(serverApi.GetSystem(modName, "main"))
        self.Register()

    def Register(self):
        for key in dir(self):
            obj = getattr(self, key)
            if callable(obj) and hasattr(obj, 'listen_event'):
                event = getattr(obj, 'listen_event')
                _type = getattr(obj, 'listen_type')
                priority = getattr(obj, 'listen_priority')
                self.ListenForEvent(event, obj, _type=_type, priority=priority)

    def ListenForEvent(self, event, func, _type, priority):
        if _type not in self.ListenDict:
            name, system = _type, "main"
        else:
            name, system = self.ListenDict[_type]
        self.system.ListenForEvent(name, system, event, self, func, priority=priority)

    def BroadcastEvent(self, eventName, eventData):
        # type: (str, dict) -> 'None'
        """
        本地广播事件，客户端system广播的事件仅客户端system能监听，服务器system广播的事件仅服务端system能监听。
        """
        self.system.BroadcastEvent(eventName, eventData)

    def BroadcastToAllClient(self, eventName, eventData):
        # type: (str, dict) -> 'None'
        """
        服务器广播事件到所有客户端
        """
        self.system.BroadcastToAllClient(eventName, eventData)

    def NotifyToMultiClients(self, targetIdList, eventName, eventData):
        # type: (List[str], str, dict) -> 'None'
        """
        服务器发送事件到指定一批客户端，相比于在for循环内使用NotifyToClient性能更好
        """
        self.system.NotifyToMultiClients(targetIdList, eventName, eventData)

    def NotifyToClient(self, targetId, eventName, eventData):
        # type: (str, str, dict) -> 'None'
        """
        服务器发送事件到指定客户端
        """
        if targetId is None:
            self.NotifyToMultiClients(serverApi.GetPlayerList(), eventName, eventData)
        self.system.NotifyToClient(targetId, eventName, eventData)

    def CreateEngineEntityByNBT(self, nbtDict, pos=None, rot=None, dimensionId=0, isNpc=False, isGlobal=None):
        # type: (dict, Union[Tuple[float,float,float],None], Union[Tuple[float,float],None], int, bool, Union[None,bool]) -> 'Union[str,None]'
        """
        根据nbt数据创建实体
        """
        self.system.CreateEngineEntityByNBT(nbtDict, pos, rot, dimensionId, isNpc, isGlobal)

    def CreateEngineEntityByTypeStr(self, engineTypeStr, pos, rot, dimensionId=0, isNpc=False, isGlobal=False):
        # type: (str, Tuple[float,float,float], Tuple[float,float], int, bool, bool) -> 'Union[str,None]'
        """
        创建指定identifier的实体
        """
        self.system.CreateEngineEntityByTypeStr(engineTypeStr, pos, rot, dimensionId, isNpc, isGlobal)

    def CreateEngineItemEntity(self, itemDict, dimensionId=0, pos=(0, 0, 0)):
        # type: (dict, int, Tuple[float,float,float]) -> 'Union[str,None]'
        """
        用于创建物品实体（即掉落物），返回物品实体的entityId
        """
        self.system.CreateEngineItemEntity(itemDict, dimensionId, pos)

    def DestroyEntity(self, entityId):
        # type: (str) -> 'bool'
        """
        销毁实体
        """
        self.system.DestroyEntity(entityId)

    def RequestToServiceMod(self, modname, method, data, callback=None, timeout=2):
        """
        给service发请求
        """
        def _callback(isSuc, args):
            print ("RequestToServiceMod callback, isSuc={} args={}".format(isSuc, args))
        self.system.RequestToServiceMod(modname, method, data, callback or _callback, timeout)
