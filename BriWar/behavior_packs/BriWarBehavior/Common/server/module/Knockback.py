# coding=utf-8
"""
Created on 2025/07/26
Knockback模块
这里主要 修改玩家kb参数
接口：
-
"""
from ..utils import *


class KnockbackModule(BaseModule):
    def __init__(self):
        super(KnockbackModule, self).__init__()
        self.power = 0.8
        self.height = 0.6
        self.heightCap = 0.3
        self.HurtCD = 5
        Game.SetHurtCD(self.HurtCD)

    @Listen()
    def DamageEvent(self, args):
        """
        实体受到伤害时触发
        :param args:
        :return:
        """
        srcId = args["srcId"]
        if not srcId:
            return
        args["knock"] = False
        rot = RotComp(srcId).GetRot()
        if not rot:
            return
        dx, dy, dz = serverApi.GetDirFromRot(rot)
        CF.CreateAction(args["entityId"]).SetMobKnockback(dx, dz, self.power, self.height, self.heightCap)

    def SetKnockback(self, args):
        """
        设置实体的击退参数
        :param args:
        :return:
        """
        data = args["data"]
        try:
            self.power = float(data["power"])
        except:
            MsgComp(args["playerId"]).NotifyOneMessage(args["playerId"], "power参数必须是小数")
        try:
            self.height = float(data["height"])
        except:
            MsgComp(args["playerId"]).NotifyOneMessage(args["playerId"], "height参数必须是小数")
        try:
            self.heightCap = float(data["heightCap"])
        except:
            MsgComp(args["playerId"]).NotifyOneMessage(args["playerId"], "heightCap参数必须是小数")
        try:
            self.HurtCD = int(data["HurtCD"])
            Game.SetHurtCD(self.HurtCD)
        except:
            MsgComp(args["playerId"]).NotifyOneMessage(args["playerId"], "HurtCD参数必须是整数")

    @Listen()
    def CommandEvent(self, args):
        """
        玩家输入指令时触发
        :param args:
        :return:
        """
        if args["command"] in ["/kb", "/Kb", "/KB", "/kB"]:
            args["cancel"] = True
            form = self.system.FormModule.GetFormBuilder("knockback调试器", "knockback")
            form.inputBox("用来控制水平方向的初速度", "请输入小数", str(self.power), "power")
            form.inputBox("竖直方向的初速度", "请输入小数", str(self.height), "height")
            form.inputBox(
                "向上速度阈值，当实体本身已经有向上的速度时需要考虑这个值，用来确保最终向上的速度不会超过heightCap",
                "请输入小数", str(self.heightCap), "heightCap")
            form.inputBox("受击冷却时间", "请输入整数", str(self.HurtCD), "HurtCD")
            form.button("保存并应用", "save")
            form.send(args["entityId"], self.SetKnockback)
