# coding=utf-8
"""
Created on 2025/07/11
表单模块
这里主要 控制游戏的表单
接口：
- GetFormBuilder(title, _id) # 获取表单构建器，返回Form对象
- Form.label(text='') # 纯文本
- Form.image(path='textures/ui/rating_screen', size=(260, 64)) # 图片
- Form.button(text='未命名按钮', tag='undefined') # 按钮
- Form.imgButton(text='未命名按钮', path='textures/ui/redX1', tag='undefined') # 左侧带图片的按钮
- Form.itemButton(text='未命名按钮', item_name='minecraft:unknown', item_aux=0, item_ench=False, tag='undefined') # 左侧带物品渲染器的按钮
- Form.inputBox(text='请输入文字:', holder='请输入内容', default='', tag='undefined') # 输入框
- Form.toggle(text='开/关', default=False, tag='undefined') # 开关
- Form.slider(text='当前值: {value}%%', start=0, end=100, step=1, default=0, tag='undefined') # 滑动栏
- Form.paperDoll(entityId='', scale=1) # 网易纸娃娃
- Form.progressBar(value=0.8, color=(0, 0.6, 1)) # 进度条
- Form.send(playerId, callback=None, data=None) # 将本表单发送给该playerId的玩家客户端
"""
from ..utils import *

class Form(object): # 表单构建器，封装表单List
    def __init__(self, system, title, _id):
        self.system = system # 表单所属的系统
        self.data = [] # 表单元数据
        self.title = title # 表单的标题
        self.boardId = _id # 表单的唯一标识

    def label(self, text=''): # 纯文本
        self.data.append({'type': 'label', 'text': text})
        return self

    def image(self, path='textures/ui/rating_screen', size=(260, 64)): # 图片
        self.data.append({'type': 'image', 'path': path, 'size': size})
        return self

    def button(self, text='未命名按钮', tag='undefined'): # 按钮
        self.data.append({'type': 'button', 'text': text, 'tag': tag})
        return self

    def imgButton(self, text='未命名按钮', path='textures/ui/redX1', tag='undefined'): # 左侧带图片的按钮
        self.data.append({'type': 'button_img', 'text': text, 'path': path, 'tag': tag})
        return self

    def itemButton(self, text='未命名按钮', item_name='minecraft:unknown', item_aux=0, item_ench=False, tag='undefined'): # 左侧带物品渲染器的按钮
        self.data.append({'type': 'button_item', 'text': text, 'item_name': item_name, 'item_aux': item_aux, 'item_ench': item_ench, 'tag': tag})
        return self

    def inputBox(self, text='请输入文字:', holder='请输入内容', default='', tag='undefined'): # 输入框
        self.data.append({'type': 'input', 'text': text, 'default': default, 'holder': holder, 'tag': tag})
        return self

    def toggle(self, text='开/关', default=False, tag='undefined'): # 开关
        self.data.append({'type': 'toggle', 'text': text, 'default': default, 'tag': tag})
        return self

    def slider(self, text='当前值: {value}%%', start=0, end=100, step=1, default=0, tag='undefined'): # 滑动栏
        if '{value}' not in text:
            text += '{value}'
        self.data.append({'type': 'slider', 'text': text,'start': start, 'end': end,'step': step, 'default': default, 'tag': tag})
        return self

    def paperDoll(self, entityId='', scale=1): # 网易纸娃娃
        self.data.append({'type': 'doll', 'entityId': entityId, 'scale': scale})
        return self

    def progressBar(self, value=0.8, color=(0, 0.6, 1)): # 进度条
        self.data.append({'type': 'progress', 'value': value, 'color': color})
        return self

    def send(self, playerId, callback=None, data=None): # 将本表单发送给该playerId的玩家客户端
        args = {
            'form': self.data, # 表单元数据
            'title': self.title, # 表单的标题
            'boardId': self.boardId, # 表单的唯一标识
            'customData': data # 自定义数据
        }
        self.system.NotifyToClient(playerId, 'sendForm', args) # 与客户端通讯，将表单数据发送给客户端
        if callback: # 如果配置回调函数了
            self.system.callbackCache[self.boardId] = callback # 将boardId - callback 映射关系存入缓存
        return self

class FormModule(BaseModule):
    def __init__(self):
        super(FormModule, self).__init__()
        self.callbackCache = {}  # 回调缓存: {boardId: function}

    def GetFormBuilder(self, title, _id):
        """
        获取表单构建器
        """
        return Form(self, title, _id)

    @Listen(event_type=Listen.client)
    def ButtonClickEvent(self, args): # 客户端点击按钮后触发该事件
        args['playerId'] = args['__id__'] # 获取客户端玩家Id
        if args['boardId'] in self.callbackCache: # 如果配置回调函数了
            self.callbackCache[args['boardId']](args) # 从缓存中找到该boardId对应的回调函数，调用并传参
