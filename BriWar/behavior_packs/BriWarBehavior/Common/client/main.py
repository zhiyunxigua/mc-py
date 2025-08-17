# -*- coding: utf-8 -*-
"""
Created on 2025-08-15
客户端系统
"""
from utils import *

NativeScreenManager = clientApi.GetNativeScreenManagerCls()

class Main(BaseSystem):
    def __init__(self, namespace, systemName):
        super(Main, self).__init__(namespace, systemName)
        self.game_info_text = "这里显示游戏信息"
        NativeScreenManager.instance().RegisterScreenProxy("hud.hud_screen", "Common.client.ui.hud_proxys.Main")

    @Listen()
    def LoadClientAddonScriptsAfter(self, args):
        self.register_module()

    def register_module(self):
        pass

    @Listen("OnLocalPlayerStopLoading")
    def client_init(self, args):
        self.NotifyToServer("OnLocalPlayerStopLoading", {})

        # 新增molang部分
        query_comp = CF.CreateQueryVariable(LevelId) # 创建queryVariable组件
        query_comp.Register('query.mod.team_red', 0.0) # 注册molang
        query_comp.Register('query.mod.team_blue', 0.0) # 注册molang
        query_comp.Register('query.mod.team_green', 0.0) # 注册molang
        query_comp.Register('query.mod.team_yellow', 0.0) # 注册molang

    @Listen("SetMolangValue", "server")
    def SetMolangValue(self, args):
        """
        设置molang变量的值
        """
        args.pop(PlayerId)
        for pid, team in args.items():
            query_comp = CF.CreateQueryVariable(pid) # 创建queryVariable组件
            query_comp.Set('query.mod.team_' + team, 1.0) # 设置molang变量的值

    @Listen()
    def UiInitFinished(self, args):
        """
        ui创建创建成功
        """
        self.NotifyToServer('UiInitFinished', dict())
        clientApi.RegisterUI(modName, 'form', "Common.client.ui.Form.Main", "form.main")

    @Listen("sendForm", Listen.server)
    def GetFormFromServer(self, args):  # 从服务端获取表单信息，将界面入栈弹出，并将信息传递给screen类
        clientApi.PushScreen(modName, 'form',
                             {'data': args, 'customData': args['customData']})
