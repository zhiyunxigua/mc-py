# coding=utf-8
modName = "BriWarMod"
version = "0.0.1"
systemName = "main"

COUNTDOWN_TIME = 20

JOIN_MESSAGE = "§a[战桥] §7{name} 加入了游戏"
LEFT_MESSAGE = "§a[战桥] §7{name} 离开了游戏"

SPAWN_POS = (0.5, 1, 0)
SPAWN_ROT = (0, 0)

RED_SPAWN_POS = (0.5, 0, 38.5)
RED_SPAWN_ROT = (0, 180)

BLUE_SPAWN_POS = (0.5, 0, -37.5)
BLUE_SPAWN_ROT = (0, 0)

ROUND_TIME = 120  # 1回合时间

ITEM_TEMPLATE = {
    "newItemName": "",
    "newAuxValue": 0,
    "count": 1
}

PLAYER_ITEMS = {
    (0, 0): dict(ITEM_TEMPLATE, newItemName="minecraft:wooden_sword"),
    (0, 3): dict(ITEM_TEMPLATE, newItemName="minecraft:shears"),
    (0, 4): dict(ITEM_TEMPLATE, newItemName="minecraft:snowball", count=16),
    (0, 5): dict(ITEM_TEMPLATE, newItemName="minecraft:bow"),
    (0, 6): dict(ITEM_TEMPLATE, newItemName="minecraft:arrow", count=8),
    (0, 7): {
        "newItemName": "minecraft:stick",
        "count": 1,
        "newAuxValue": 0,
        "userData": {
            "ench": [{"lvl": {"__type__": 2, "__value__": 2},
                     "id": {"__type__": 2, "__value__": 12}}],
            "display": {"Name": {"__type__": 8, "__value__": "§r§b击退棒"}}
        }
    },
    (0, 8): dict(ITEM_TEMPLATE, newItemName="minecraft:golden_apple")
}

def create_team_data(name, color):
    return {
        "minecraft:item_lock": {"__type__": 1, "__value__": 1},
        "display": {'Name': {'__type__': 8, '__value__': name}},
        "customColor": {'__type__': 3, '__value__': color}
    }

RED_DATA = create_team_data("§c红队", 0x8A1200)
BLUE_DATA = create_team_data("§b蓝队", 0x313DB1)

RED_WOOL_ITEMS = {
    (0, 1): dict(ITEM_TEMPLATE, newItemName="minecraft:red_wool", count=128),
    (0, 2): dict(ITEM_TEMPLATE, newItemName="minecraft:red_wool", count=128)
}

BLUE_WOOL_ITEMS = {
    (0, 1): dict(ITEM_TEMPLATE, newItemName="minecraft:blue_wool", count=128),
    (0, 2): dict(ITEM_TEMPLATE, newItemName="minecraft:blue_wool", count=128)
}
def create_team_armor(team_data):
    armor_types = [
        "minecraft:leather_helmet",
        "minecraft:leather_chestplate",
        "minecraft:leather_leggings",
        "minecraft:leather_boots"
    ]
    return {
        (3, i): dict(ITEM_TEMPLATE, newItemName=armor_type, userData=team_data)
        for i, armor_type in enumerate(armor_types)
    }

RED_ARROW = create_team_armor(RED_DATA)
BLUE_ARROW = create_team_armor(BLUE_DATA)

# 合并红队物品
RED_PLAYER_ITEMS = PLAYER_ITEMS.copy()
RED_PLAYER_ITEMS.update(RED_WOOL_ITEMS)
RED_PLAYER_ITEMS.update(RED_ARROW)

# 合并蓝队物品
BLUE_PLAYER_ITEMS = PLAYER_ITEMS.copy()
BLUE_PLAYER_ITEMS.update(BLUE_WOOL_ITEMS)
BLUE_PLAYER_ITEMS.update(BLUE_ARROW)