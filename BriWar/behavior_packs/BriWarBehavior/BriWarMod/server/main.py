# -*- coding: utf-8 -*-
"""
Created on 2025-08-15
服务端系统
"""
from utils import *
from .module.GameRule import GameRuleModule
from StateBase import StateMode, FSM
from states import *


class Main(BaseServer):
    def __init__(self, namespace, systemName):
        super(Main, self).__init__(namespace, systemName)
        self.GameRule = None

        self.fsm = FSM()

    @Listen()
    def LoadServerAddonScriptsAfter(self, args):
        self.register_module()  # 注册模块
        self.register_state()  # 注册状态机

    def register_module(self):
        self.GameRule = GameRuleModule()

    @property
    def Common(self):
        common = serverApi.GetSystem("Common", "main")
        if common is None:
            return None
        return weakref.proxy(common)

    def register_state(self):
        self.fsm.add_state(waiting.WaitingState)  # 添加状态
        self.fsm.add_state(gaming.GamingState)  # 添加状态
        self.fsm.add_state(gameover.GameOverState)  # 添加状态
        self.fsm.update_state(StateMode.waiting)  # 更新状态
