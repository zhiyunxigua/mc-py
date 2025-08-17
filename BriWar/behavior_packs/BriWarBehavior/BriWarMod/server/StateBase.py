# coding=utf-8
from utils import *
import weakref


class StateMode():
    """状态模式枚举类，定义所有可能的主状态"""
    waiting = "waiting"  # 等待状态
    gaming = "gaming"  # 游戏进行状态
    gameover = "gameover"  # 游戏结束状态


class BaseState(ServerSystem):
    """
    状态基类，所有具体状态都应继承此类
    实现了基本的状态管理功能和事件监听机制
    """

    enabled = None  # 状态是否启用标志
    state_name = None  # 状态名称，子类必须设置
    system = None  # 系统引用
    fsm = None  # 所属状态机引用
    parent_state = None  # 父状态引用（用于子状态）

    # 事件监听配置字典，定义不同类型事件的监听目标
    ListenDict = {
        Listen.Minecraft: ("Minecraft", "Engine"),
        Listen.client: (modName, "main"),
        Listen.server: (modName, "main")
    }

    def __init__(self, namespace, name):
        """
        初始化状态
        :param namespace: 命名空间
        :param name: 系统名称
        """
        super(BaseState, self).__init__(namespace, name)
        # 获取系统弱引用，避免循环引用导致内存泄漏
        self.system = weakref.proxy(serverApi.GetSystem(modName, systemName))
        self.sub_states = set()  # 子状态集合

    def _on_enable(self, *args, **kwargs):
        """
        内部启用状态方法
        1. 先禁用所有监听器（清理状态）
        2. 注册所有事件监听器
        3. 调用子类的on_enable方法
        """
        self.enabled = True
        self._on_disable(*args, **kwargs)  # 先禁用所有监听器（清理状态）

        # 注册所有事件监听器
        self.Register()

        self.on_enable(*args, **kwargs)  # 调用子类实现的启用逻辑

    def _on_disable(self, *args, **kwargs):
        """
        内部禁用状态方法
        1. 取消所有事件监听
        2. 禁用所有子状态
        3. 调用子类的on_disable方法
        """
        self.enabled = False

        # 取消所有事件监听
        self.UnListenAllEvents()

        # 递归禁用所有子状态
        for state in self.sub_states:
            state._on_disable(*args, **kwargs)

        self.on_disable(*args, **kwargs)  # 调用子类实现的禁用逻辑

    def on_enable(self, *args, **kwargs):
        """子类应重写此方法实现状态启用时的逻辑"""
        pass

    def on_disable(self, *args, **kwargs):
        """子类应重写此方法实现状态禁用时的逻辑"""
        pass

    def Register(self):
        """
        自动注册带有监听器注解的方法
        遍历类的所有属性，检查是否有监听器注解
        """
        for key in dir(self):
            obj = getattr(self, key)
            # 检查方法是否有listen_event属性（被监听器装饰器装饰过）
            if callable(obj) and hasattr(obj, 'listen_event'):
                event = getattr(obj, 'listen_event')  # 获取事件名称
                _type = getattr(obj, 'listen_type')  # 获取事件类型
                priority = getattr(obj, 'listen_priority')  # 获取监听优先级
                self.listen(event, obj, _type, priority)

    def listen(self, event, func, _type, priority):
        """
        注册事件监听器
        :param event: 事件名称
        :param func: 回调函数
        :param _type: 事件类型
        :param priority: 监听优先级
        """
        # 从ListenDict中获取实际的系统名称和命名空间
        if _type not in self.ListenDict:
            name, system = _type, "main"  # 默认值
        else:
            name, system = self.ListenDict[_type]

        self.ListenForEvent(name, system, event, self, func, priority)

    def unlisten(self, event, func, _type, priority):
        """
        取消事件监听
        :param event: 事件名称
        :param func: 回调函数
        :param _type: 事件类型
        :param priority: 监听优先级
        """
        # 从ListenDict中获取实际的系统名称和命名空间
        if _type not in self.ListenDict:
            name, system = _type, "main"  # 默认值
        else:
            name, system = self.ListenDict[_type]

        self.UnListenForEvent(name, system, event, self, func, priority)

    def add_sub_state(self, state_type, *args, **kwargs):
        """
        添加子状态
        :param state_type: 子状态类
        :return: 创建的子状态实例
        """
        state = state_type(modName, systemName)
        state.fsm = self.fsm or self  # 子状态继承父状态的FSM
        state.parent_state = self  # 设置父状态引用
        self.sub_states.add(state)  # 添加到子状态集合
        return state

    def start_sub_state(self, state_name, *args, **kwargs):
        """
        激活指定的子状态（禁用其他子状态）
        :param state_name: 要激活的子状态名称
        """
        for state in self.sub_states:
            if state.state_name == state_name:
                state._on_enable(*args, **kwargs)
                logger.debug("Enable sub-state {} under {}".format(state.state_name, self.state_name))
            else:
                state._on_disable()
                logger.debug("Disable sub-state {} under {}".format(state.state_name, self.state_name))

    def reset_sub_state(self, state_name, *args, **kwargs):
        pass

    def end_sub_state(self, state_name, *args, **kwargs):
        pass

class FSM:
    """有限状态机（Finite State Machine）类，管理状态切换和状态生命周期"""

    def __init__(self):
        """初始化状态机"""
        self.states = set()  # 所有已注册的状态集合
        self.now_state = set()  # 当前活跃的状态集合（通常只有一个）
        self.system = None  # 系统引用

    def add_state(self, state_type, is_sub_state=False, parent_state=None, *args, **kwargs):
        """
        添加状态到状态机
        :param state_type: 状态类
        :param is_sub_state: 是否为子状态
        :param parent_state: 父状态实例（如果是子状态）
        :return: 创建的状态实例
        """
        if is_sub_state and parent_state:
            # 如果是子状态，添加到父状态中
            return parent_state.add_sub_state(state_type, *args, **kwargs)
        else:
            # 否则作为顶级状态添加到状态机
            state = state_type(modName, systemName)
            state.fsm = self  # 设置状态机的引用
            self.states.add(state)
            return state

    def update_state(self, new_state, *args, **kwargs):
        """
        更新当前状态
        :param new_state: 要切换到的状态名称
        """
        logger.info("FSM: state changed to {}".format(new_state))

        # 遍历所有状态，启用匹配的状态，禁用其他状态
        for state in self.states:
            if state.state_name == new_state:
                state._on_enable(*args, **kwargs)
                logger.debug("Enable state {}".format(state.state_name))
                self.now_state.add(state)
            else:
                state._on_disable()
                logger.debug("Disable state {}".format(state.state_name))
                self.now_state.discard(state)

    def get_state(self):
        """
        获取当前活跃的状态
        :return: 当前状态实例，如果没有活跃状态则返回None
        """
        return next(iter(self.now_state)) if self.now_state else None

    def get_active_sub_state(self, parent_state=None):
        """
        获取当前活跃的子状态
        :param parent_state: 父状态实例，如果为None则使用当前活跃状态
        :return: 活跃的子状态实例，如果没有则返回None
        """
        if parent_state is None:
            parent_state = self.get_state()

        if parent_state:
            # 在父状态的子状态中查找启用的状态
            for state in parent_state.sub_states:
                if state.enabled:
                    return state
        return None
