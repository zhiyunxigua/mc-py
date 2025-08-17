# coding=utf-8
"""
Created on 2025-08-15
游戏规则模块
这里主要 开局初始化游戏规则
接口：
-
"""
from ..utils import *

gameRuleDict = {
    'option_info': {
        'pvp': True,  # 玩家间伤害
        'show_coordinates': True,  # 显示坐标
        'fire_spreads': False,  # 火焰蔓延
        'tnt_explodes': False,  # TNT爆炸
        'mob_loot': False,  # 生物战利品
        'natural_regeneration': True,  # 自然生命恢复
        'respawn_block_explosion': False,  # 重生方块爆炸
        'respawn_radius': 0,  # 重生半径，请注意范围,目前支持[0,128]
        'tile_drops': True,  # 方块掉落
        'immediate_respawn': True  # 立即重生
    },
    'cheat_info': {
        'enable': True,  # 激活作弊
        'always_day': True,  # 终为白日
        'mob_griefing': False,  # 生物破坏
        'keep_inventory': True,  # 保留物品栏
        'weather_cycle': False,  # 天气更替
        'mob_spawn': False,  # 生物生成
        'entities_drop_loot': False,  # 实体掉落战利品
        'daylight_cycle': False,  # 开启昼夜更替
        'command_blocks_enabled': False,  # 启用命令方块
        'random_tick_speed': 1,  # 随机刻速度
    }
}


class GameRuleModule(BaseModule):

    def __init__(self):
        super(GameRuleModule, self).__init__()

    @Listen()
    def ClientLoadAddonsFinishServerEvent(self, args):
        Game.SetGameRulesInfoServer(gameRuleDict)  # 设置游戏规则
        Game.SetGameDifficulty(1)  # 设置游戏难度简单
        Game.SetDefaultGameType(minecraftEnum.GameType.Survival)
        # self.SetRules('showDeathMessages', 'false')  # 隐藏玩家死亡信息提示
        Game.LockDifficulty(True)  # 锁定游戏难度

    def SetRules(self, rule, value):
        """
        设置游戏规则指令
        :param rule: 规则名
        :param value: 规则值
        """
        Game.LockGameRulesInfo(False)
        success = CommandComp.SetCommand('gamerule {} {}'.format(rule, value))
        Game.LockGameRulesInfo(True)
        return success
