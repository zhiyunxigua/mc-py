# -*- coding: utf-8 -*-
"""
Created on 2025-08-15
模板UI系统
这里主要 提供一个模板
"""
from utils import *


class Main(BaseCustomScreen):
    def __init__(self, namespace, name, param):
        super(Main, self).__init__(namespace, name, param)

    def Create(self): # 当界面加载完成后
        pass

    def OnActive(self):  # UI重新回到栈顶时调用
        pass

    def OnDeactive(self):  # 栈顶UI有其他UI入栈时调用
        pass

    def Destroy(self):  # 销毁时调用
        pass
