# -*- encoding: utf-8 -*-
import time, math, mod.client.extraClientApi as clientApi, mod.common.minecraftEnum as enum, random, weakref
from mod_log import logger as logger
from .config import *
ClientSystem = clientApi.GetClientSystemCls()
CF = clientApi.GetEngineCompFactory()
LevelId = clientApi.GetLevelId()
PlayerId = clientApi.GetLocalPlayerId()

Game = CF.CreateGame(LevelId)
PosComp = CF.CreatePos(PlayerId)
RotComp = CF.CreateRot(PlayerId)
TextBoardComp = CF.CreateTextBoard(PlayerId)
Music = CF.CreateCustomAudio(LevelId)
NameComp = CF.CreateName(PlayerId)
ItemComp = CF.CreateItem(PlayerId)

PlayerName = NameComp.GetName()

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

class BaseSystem(ClientSystem):
    ListenDict = {"Minecraft": ("Minecraft", "Engine"), "client": (modName, "main"), "server": (modName, "main")}
    def __init__(self, namespace, systemName):
        super(BaseSystem, self).__init__(namespace, systemName)
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
        self.system = weakref.proxy(clientApi.GetSystem(modName, "main"))
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

    def NotifyToServer(self, eventName=str(), eventData=None):
        # type: (str, dict) -> 'None'
        """
        给服务端发送事件
        """
        self.system.NotifyToServer(eventName, eventData)

    def BroadcastEvent(self, eventName=str(), eventData=None):
        # type: (str, dict) -> 'None'
        """
        本地广播事件，客户端system广播的事件仅客户端system能监听，服务器system广播的事件仅服务端system能监听。
        """
        self.system.BroadcastEvent(eventName, eventData)


    def CreateEngineSfx(self, path, pos=None, rot=None, scale=None):
        # type: (str, Tuple[float,float,float], Tuple[float,float,float], Tuple[float,float,float]) -> 'Union[int,None]'
        """
        创建序列帧特效
        """
        self.system.CreateEngineSfx(path, pos, rot, scale)

    def CreateEngineSfxFromEditor(self, path, pos=None, rot=None, scale=None):
        # type: (str, Tuple[float,float,float], Tuple[float,float,float], Tuple[float,float,float]) -> 'Union[int,None]'
        """
        指使用资源包中effects/xxx.json，按照编辑器中编辑好的参数创建序列帧。支持环状序列帧
        """
        self.system.CreateEngineSfxFromEditor(path, pos, rot, scale)

    def CreateEngineParticle(self, path, pos):
        # type: (str, Tuple[float,float,float]) -> 'Union[int,None]'
        """
        用于创建粒子特效
        """
        self.system.CreateEngineParticle(path, pos)

    def CreateEngineEffectBind(self, path, bindEntity, aniName):
        # type: (str, str, str) -> 'Union[int,None]'
        """
        指用编辑器保存资源包中models/bind/xxx_bind.json生成编辑好的所有挂点的所有特效。生成的特效会自动进行挂接及播放，编辑器中设为不可见的特效也会进行播放。并且使用这种方式创建的特效，开发者不用维护entity进出视野导致的挂接特效被移除，引擎会在entity每次进入视野时自动创建所有特效。
        """
        self.system.CreateEngineEffectBind(path, bindEntity, aniName)

    def DestroyEntity(self, entityId):
        # type: (int) -> 'bool'
        """
        销毁特效
        """
        pass

    def CreateClientEntityByTypeStr(self, engineTypeStr, pos, rot):
        # type: (str, Tuple[float,float,float], Tuple[float,float]) -> 'Union[str,None]'
        """
        创建客户端实体
        """
        self.system.CreateClientEntityByTypeStr(engineTypeStr, pos, rot)

    def DestroyClientEntity(self, entityId):
        # type: (str) -> 'None'
        """
        销毁客户端实体
        """
        self.system.DestroyClientEntity(entityId)

