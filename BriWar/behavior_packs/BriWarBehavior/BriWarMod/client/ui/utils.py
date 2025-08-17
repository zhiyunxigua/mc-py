# -*- encoding: utf-8 -*-
from ..utils import *
import re
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
BP0 = '/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix'
BP = BP0+'/safezone_screen_panel/root_screen_panel'


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


class BaseCustomScreen(ScreenNode):
    ListenDict = {"Minecraft": ("Minecraft", "Engine"), "client": (modName, "main"), "server": (modName, "main")}
    system = None
    def __init__(self, namespace, name, param):
        super(BaseCustomScreen, self).__init__(namespace, name, param)
        self.system = weakref.proxy(clientApi.GetSystem(modName, "main"))
        self.Register()
        self._tempPos = ()
        self._moveTimer = 0
        self._touchPosX = 0
        self._touchPosY = 0
        self._screenSize = Game.GetScreenSize
        self._moveableWidgets = {}

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
        """
        给服务器发送事件通知
        """
        self.system.NotifyToServer(eventName, eventData)

    def SetPosInSafetyZone(self, path, pos=None):
        if not pos: pos = self.GetPosition(path)
        size = self.GetSize(path)
        safeSize = self.GetSize(BP)
        safeSize = (safeSize[0]-size[0],safeSize[1]-size[1])
        pos = tuple(max(min(safeSize[n], pos[n]), 0)for n in(0, 1))
        self.SetPosition(path, pos)
        customKey = self._moveableWidgets.get(path)
        if not customKey:
            return
        savedPos = CF.CreateConfigClient(LevelId).GetConfigData(customKey, True)
        savedPos[path] = pos
        CF.CreateConfigClient(LevelId).SetConfigData(customKey, savedPos, True)

    def AddMoveableButton(self, path, callBack, customKey, moveParient=False):
        realPath = path.rsplit('/', 1)[0] if moveParient else path
        self._moveableWidgets[realPath] = customKey
        savedPos = CF.CreateConfigClient(LevelId).GetConfigData(customKey, True).get(realPath)
        CF.CreateGame(LevelId).AddTimer(0, self.SetPosInSafetyZone, realPath, savedPos)
        def MoveButton(args):
            touchEvent = args['TouchEvent']
            if touchEvent == 0:
                nowPos = self.GetPosition(realPath)
                if self._moveTimer>0 or nowPos==self._tempPos:
                    self._moveTimer = 0
                    callBack(args)
                else:
                    self.SetPosInSafetyZone(realPath, nowPos)
            elif touchEvent == 1:
                self._moveTimer = 30
                self._tempPos = self.GetPosition(realPath)
                self._touchPosX, self._touchPosY = args['TouchPosX'], args['TouchPosY']
            elif self._moveTimer == 0 and touchEvent == 4:
                x, y = args['TouchPosX'], args['TouchPosY']
                tempPos = self.GetPosition(realPath)
                self.SetPosition(realPath, (x-self._touchPosX+tempPos[0], y-self._touchPosY+tempPos[1]))
                self._touchPosX, self._touchPosY = x, y
            elif self._moveTimer>0 and touchEvent == 6:
                self._moveTimer = 32767
        self.AddTouchEventHandler(path, MoveButton, {'isSwallow': True})

    def Update(self):
        screenSize = Game.GetScreenSize()
        if screenSize!=self._screenSize:
            for path in self._moveableWidgets:
                self.SetPosInSafetyZone(path)
            self._screenSize = screenSize
        if self._moveTimer:
            self._moveTimer -= 1
            if self._moveTimer==0:
                CF.CreateDevice(PlayerId).SetDeviceVibrate(25)
                CF.CreateGame(PlayerId).SetTipMessage('你正在拖动按钮')
CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
class BaseCustomScreenProxy(CustomUIScreenProxy):
    ListenDict = {"Minecraft": ("Minecraft", "Engine"), "client": (modName, "main"), "server": (modName, "main")}
    system = None
    screen = None
    def __init__(self, screenName, screenNode):
        super(BaseCustomScreenProxy, self).__init__(screenName, screenNode)
        self.system = weakref.proxy(clientApi.GetSystem(modName, "main"))
        self.screen = screenNode
        self.Register()

    def OnCreate(self):
        pass

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
