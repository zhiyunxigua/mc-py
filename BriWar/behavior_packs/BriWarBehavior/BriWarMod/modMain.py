# -*- coding: utf-8 -*-
from mod.common.mod import Mod

from server import config as server_config
import mod.server.extraServerApi as serverApi
@Mod.Binding(name=server_config.modName, version=server_config.version)
class XiGua_server(object):
    @Mod.InitServer()
    def serverInit(self):
        path = "{}.server.main.Main".format(server_config.modName)
        serverApi.RegisterSystem(server_config.modName, server_config.systemName, path)
        print ("======Init{}Server======".format(server_config.modName))

import mod.client.extraClientApi as clientApi
from client import config as client_config
@Mod.Binding(name=client_config.modName, version=client_config.version)
class XiGua_client(object):
    @Mod.InitClient()
    def clientInit(self):
        path = "{}.client.main.Main".format(client_config.modName)
        clientApi.RegisterSystem(client_config.modName, client_config.systemName, path)
        print ("======Init{}Client======".format(client_config.modName))
