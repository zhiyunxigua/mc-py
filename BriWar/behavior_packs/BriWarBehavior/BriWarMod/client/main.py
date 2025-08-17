# -*- coding: utf-8 -*-
"""
Created on 2025-08-15
客户端系统
"""
from utils import *
from .module.Template import TemplateModule


class Main(BaseSystem):
    def __init__(self, namespace, systemName):
        super(Main, self).__init__(namespace, systemName)
        self.Template = None

    @Listen()
    def LoadClientAddonScriptsAfter(self, args):
        self.register_module()

    def register_module(self):
        self.Template = TemplateModule()

    @Listen()
    def OnLocalPlayerStopLoading(self, args):
        self.NotifyToServer("OnLocalPlayerStopLoading", {})

