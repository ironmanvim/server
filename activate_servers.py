import os
import sys

os.chdir("Z:/server/")
sys.path.extend(['Z:\\server', 'Z:/server'])
import server

handler = server.VConfigHandler()

servers_list = []
for i in handler.servers:
    s = server.VHttpServer(i['name'], '', i['port'], i['work-folder'])

    server.RunParallel(s.activate_server).start()
    servers_list.append(s)
