from threading import Thread

import server, serverWS

if __name__ == '__main__':
    #Thread(target=server.main).start()
    print(server.events)
    Thread(target=serverWS.main, args=(server.events,)).start()
    server.main()
