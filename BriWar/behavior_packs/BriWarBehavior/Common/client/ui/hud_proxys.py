# -*- coding: utf-8 -*-
from utils import *

class Main(BaseCustomScreenProxy):
    def __init__(self, screenName, screenNode):
        super(Main, self).__init__(screenName, screenNode)
        self.ui_create = False
        self.PlayerPosInfo = {}  # 玩家位置信息 {"players_pos": {"1": (0, 0, 0)}}
        self.scoreboard_text_dict = dict()
        self.NewPingValue = 0
        self.ping_value = "§c无法与服务器连接"
        self.CPS_left_click_set = []
        self.CPS_right_click_set = []
        self.player_info_visible = False
        self.DanmakuCache = {1: 0, 2: 0, 3: 0}
        # 弹幕轨道配置
        self.font_height = 15  # 弹幕字体高度
        self.top_margin = 20  # 顶部安全区
        self.track_count = 5  # 5个轨道
        self.track_offset_range = 2  # 每条弹幕的随机上下偏移范围（±2px）
        
    def OnCreate(self):
        self.ui_create = True
        if self.screen is None:
            return
        
        # 计算每个轨道的基准Y坐标
        self.track_base_positions = [
            self.top_margin + (i * self.font_height)
            for i in range(self.track_count)
        ]

        # 轨道占用管理（记录弹幕结束时间）
        self.track_available_time = [0] * self.track_count  # 轨道可再次使用的时间戳
        self.track_available_time_top = [0] * self.track_count  # 轨道可再次使用的时间戳

        panel = self.screen.GetBaseUIControl(BP)
        self.child = self.screen.CreateChildControl("hud_ui.root_panel_watermelon", "root_panel_watermelon", panel)
        self.PlayerPosSlider = self.screen.GetBaseUIControl(
            BP + "/root_panel_watermelon/player_position_bar").asSlider()
        self.DanmakuPanel = self.screen.GetBaseUIControl(BP + "/root_panel_watermelon/danmaku")
        # self.SetScoreboard({"title": "分数板", "order": ("1", "2", "3"), "text_dict": {"1": "志云工作室", "2": "测试", "3": "TEST"}})
        self.screen.GetBaseUIControl(
            BP + "/root_panel_watermelon/player_info/frame").asImage().SetSpritePlatformFrame()
        self.screen.GetBaseUIControl(
            BP + "/root_panel_watermelon/player_info/frame/head").asImage().SetSpritePlatformHead()
        self.screen.GetBaseUIControl(
            BP + "/root_panel_watermelon/player_info/lvl_and_name/name").asLabel().SetText(PlayerName)
        self.screen.GetBaseUIControl(BP + "/root_panel_watermelon/player_info").asImage().SetVisible(False)

    @Listen("NewDanmaku", "server")
    def OnNewDanmaku(self, args):
        message = args["message"]
        danmaku_type = args.get("danmaku_type", "scroll")
        background = args.get("background")
        if danmaku_type == "scroll":
            self.CreateScrollDanmaku(message, background)
        elif danmaku_type == "top":
            self.CreateTopDanmaku(message, background)

    def CreateScrollDanmaku(self, message, background):
        child_name = "danmaku_text_{}".format(time.time())
        child = self.screen.CreateChildControl("hud_ui.danmaku_text", child_name, self.DanmakuPanel)
        screen_width, screen_height = Game.GetScreenSize()
        size_x = child.GetFullSize("x")["absoluteValue"]
        size_y = self.font_height  # 固定高度15px

        # 1. 智能选择轨道（LRU策略：优先选择最久未使用的轨道）
        current_time = time.time()
        track_index = min(range(self.track_count), key=lambda i: self.track_available_time[i])
        
        # 2. 计算弹幕的Y坐标（基准轨道位置 + 随机偏移）
        base_y = self.track_base_positions[track_index]
        random_offset = random.randint(-self.track_offset_range, self.track_offset_range)
        final_y = max(self.top_margin, min(base_y + random_offset, screen_height - size_y))  # 确保不超出屏幕
        
        # 3. 计算动画时长和轨道占用时间
        speed = random.randint(5) * 0.01 + 0.03  # 像素/ms（可调整弹幕速度）
        animation_duration = (screen_width + size_x) * speed
        self.track_available_time[track_index] = current_time + animation_duration

        # 4. 设置动画
        animation = {
            "namespace": "danmaku",
            "danmaku_text_offset": {
                "anim_type": "offset",
                "duration": animation_duration,
                "from": [screen_width, final_y],
                "to": [0 - size_x, final_y],
                "next": "",
            },
        }
        clientApi.RegisterUIAnimations(animation)

        def callback():
            self.screen.RemoveChildControl(child)

        child.SetAnimEndCallback("danmaku_text_offset", callback)
        child.SetAnimation("offset", "danmaku", "danmaku_text_offset", True)
        if background:
            child.SetSprite(background)
        text = child.GetChildByPath("/text").asLabel()
        text.SetText(message)
    
    def CreateTopDanmaku(self, message, background):
        child_name = "danmaku_text_{}".format(time.time())
        child = self.screen.CreateChildControl("hud_ui.danmaku_text", child_name, self.DanmakuPanel)
        track_index = min(range(self.track_count), key=lambda i: self.track_available_time_top[i])
        
        # 计算弹幕的Y坐标
        base_y = self.track_base_positions[track_index] - self.top_margin
        screen_width, screen_height = Game.GetScreenSize()
        size_x = child.GetFullSize("x")["absoluteValue"]
        base_x = ((screen_width - size_x) / 2)
        if background:
            child.SetSprite(background)
        text = child.GetChildByPath("/text").asLabel()
        text.SetText(message)
        child.SetPosition(base_x, base_y)
        def callback():
            self.screen.RemoveChildControl(child)
        Game.AddTimer(7, callback)

    @Listen("SetPlayerInfoVisible", "server")
    def OnSetPlayerInfoVisible(self, visible):
        self.player_info_visible = visible
        if self.ui_create:
            self.screen.GetBaseUIControl(BP + "/root_panel_watermelon/player_info").asImage().SetVisible(visible)

    @Listen("LeftClickBeforeClientEvent")
    def OnLeftClickBeforeClientEvent(self, args):
        self.CPS_left_click_set.append(time.time())

    @Listen("TapBeforeClientEvent")
    def OnTapBeforeClientEvent(self, args):
        self.CPS_left_click_set.append(time.time())

    @Listen("RightClickBeforeClientEvent")
    def OnRightClickBeforeClientEvent(self, args):
        self.CPS_right_click_set.append(time.time())

    @Listen("players_pos", "server")
    def OnPlayerPosChange(self, args):
        self.PlayerPosInfo = args

    @Listen("ping_value", "server")
    def OnPingValueChange(self, value):
        self.NewPingValue = int((time.time() * 1000 - value))
        if self.NewPingValue < 20:
            self.NewPingValue = 20
        if self.NewPingValue > 1000:
            self.NewPingValue = 1000

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#player_info.visible")
    def return_player_info_visible(self):
        return self.player_info_visible

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#input_mode.keyboard_and_mouse")
    def return_input_mode_keyboard_and_mouse(self):
        if CF.CreatePlayerView(PlayerId).GetToggleOption("INPUT_MODE") == 0:
            return True
        return False

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#input_mode.touch")
    def return_input_mode_touch(self):
        if CF.CreatePlayerView(PlayerId).GetToggleOption("INPUT_MODE") == 1:
            return True
        return False

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#input_mode.controller")
    def return_input_mode_controller(self):
        if CF.CreatePlayerView(PlayerId).GetToggleOption("INPUT_MODE") == 2:
            return True
        return False

    @ViewBinder.binding(ViewBinder.BF_BindString, "#game_info.text")
    def return_game_info_text(self):
        return self.system.game_info_text

    @ViewBinder.binding(ViewBinder.BF_BindString, "#FPS_value")
    def return_FPS_value(self):
        return "FPS:{}".format(int(Game.GetFps()))

    @ViewBinder.binding(ViewBinder.BF_BindString, "#CPS_value")
    def return_CPS_value(self):
        now = time.time()
        for left in self.CPS_left_click_set:
            if now - left > 1:
                self.CPS_left_click_set.remove(left)
                continue
        for right in self.CPS_right_click_set:
            if now - right > 1:
                self.CPS_right_click_set.remove(right)
                continue
        left_cps = len(self.CPS_left_click_set)
        right_cps = len(self.CPS_right_click_set)
        if (left_cps >= 30) or (right_cps >= 30):
            self.system.NotifyToServer("CPS_high", {"L": left_cps, "R": right_cps})
        if left_cps == 0 and right_cps == 0:
            return ""
        elif left_cps == 0:
            return "CPS:0|{}".format(right_cps)
        elif right_cps == 0:
            return "CPS:{}".format(left_cps)
        else:
            return "CPS:{}|{}".format(left_cps, right_cps)

    @ViewBinder.binding(ViewBinder.BF_BindString, "#ping_value")
    def return_ping_value(self):
        ping_list = sorted(PING_ICONS.keys())
        if int(time.time()) % 5 == 0:
            self.ping_value = "§c无法与服务器连接"
            for ping in ping_list:
                if self.NewPingValue <= ping:
                    self.ping_value = "{}{}ms".format(PING_ICONS[ping]["color"], self.NewPingValue)
                    break
        return self.ping_value

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#exp_bar_box.visible")
    def return_exp_bar_box_visible(self):
        return True if self.PlayerPosInfo else False

    def OnTick(self):
        if not self.ui_create:
            return
        if self.PlayerPosInfo.get("players_pos") is None:
            return
        players_pos = self.PlayerPosInfo.get("players_pos", {})
        team_data = self.PlayerPosInfo.get("team_data", {})
        my_pos = PosComp.GetPos()
        min_distance, nearest_pid = self.find_nearest_player_distance_and_name(my_pos, players_pos)

        if not nearest_pid:
            return


        # 计算目标方向向量
        target_pos = players_pos[nearest_pid]
        dx = target_pos[0] - my_pos[0]
        dz = target_pos[2] - my_pos[2]

        # 计算世界角度（+Z 是 0°，+X 是 90°）
        world_angle_deg = math.degrees(math.atan2(dx, dz))

        # 计算相对于你的旋转的角度
        relative_angle_deg = world_angle_deg - RotComp.GetRot()[1]
        relative_angle_deg = (relative_angle_deg + 180) % 360 - 180  # 规范化到 [-180°, 180°]

        # 映射到 [0.0, 1.0]：
        # - -90° → 0.0（最左）
        # - 0° → 0.5（正前）
        # - +90° → 1.0（最右）
        # 超出 ±90° 则限制在 0.0 或 1.0
        if relative_angle_deg < -90:
            normalized_pos = 0.0
        elif relative_angle_deg > 90:
            normalized_pos = 1.0
        else:
            normalized_pos = 0.5 + (relative_angle_deg / 180.0)

        self.PlayerPosSlider.SetSliderValue(normalized_pos)


    def find_nearest_player_distance_and_name(self, my_pos, players_pos):
        min_distance = float('inf')
        entity_id = ""

        for pid, pos in players_pos.items():
            if pid == PlayerId:
                continue

            distance = math.sqrt((pos[0] - my_pos[0]) ** 2 +
                                 (pos[1] - my_pos[1]) ** 2 +
                                 (pos[2] - my_pos[2]) ** 2)

            if distance < min_distance:
                min_distance = distance
                entity_id = pid

        return min_distance if min_distance != float('inf') else None, entity_id


    @Listen("SetScoreboard", "server")
    def SetScoreboard(self, args):
        """
        设置分数板数据
        """
        self.scoreboard_text_dict = args

    def AddScoreboardText(self, name, text):
        """
        创建分数板文本
        """
        order = self.scoreboard_text_dict.setdefault("order", (name,))
        order = list(order)
        order.append(name)
        text_dict = self.scoreboard_text_dict.setdefault("text_dict", {})
        text_dict[name] = text
        self.scoreboard_text_dict["order"] = tuple(order)
        self.scoreboard_text_dict["text_dict"] = text_dict

    def RemoveScoreboardText(self, name):
        """
        移除分数板文本
        """
        order = self.scoreboard_text_dict.get("order", ())
        text_dict = self.scoreboard_text_dict.get("text_dict", {})
        if name in order:
            order = list(order)
            order.remove(name)
            self.scoreboard_text_dict["order"] = tuple(order)
        if name in text_dict:
            text_dict.pop(name)
            self.scoreboard_text_dict["text_dict"] = text_dict

    @Listen(event_type=Listen.server)
    def SetScoreboardText(self, args):
        """
        设置分数板文本
        """
        text_dict = self.scoreboard_text_dict.setdefault("text_dict", {})
        text_dict[args["name"]] = args["text"]
        self.scoreboard_text_dict["text_dict"] = text_dict

    @Listen(event_type=Listen.server)
    def SetScoreboardTitle(self, title):
        """
        设置分数板文本
        """
        self.scoreboard_text_dict["title"] = title

    @ViewBinder.binding(ViewBinder.BF_BindBool, "#scoreboard_panel.visible")
    def return_scoreboard_visible(self):
        if self.scoreboard_text_dict.get("order"):
            return True
        else:
            return False

    @ViewBinder.binding(ViewBinder.BF_BindString, "#scoreboard_panel.title")
    def return_scoreboard_title(self):
        return self.scoreboard_text_dict.get("title", "")

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#scoreboard_panel.item_count")
    def return_scoreboard_item_count(self):
        return len(self.scoreboard_text_dict.get("order", ""))

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "scoreboard_collection", "#scoreboard_panel.text")
    def return_scoreboard_text(self, index):
        try:
            item_id = self.scoreboard_text_dict.get("order", "")[index]
            return self.scoreboard_text_dict.get("text_dict", {}).get(item_id, "无")
        except IndexError:
            return "溢出"
        except Exception:
            return "未知错误"

    def OnDestroy(self):
        """
        @description UI销毁时调用
        """
        self.screen.RemoveChildControl(self.child)
        self.ui_create = False

