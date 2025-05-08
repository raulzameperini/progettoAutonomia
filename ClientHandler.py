import threading

class ClientHandler(threading.Thread):
    def __init__(self, clientSocket, clientAddress, clients):

        self.__clients = clients
        self.__clientSocket = clientSocket
        self.__clientAddress = clientAddress

        self.__mutex = threading.Lock()

    def Write(self, message):
        with self.__mutex:
            self.__clientSocket.send(message)

    def run(self):
        try:
            
            while True:
                data = self.__clientSocket.recv(1500)

                if not data:
                    break
                
                message = data.decode("UTF-8")
                for k, ch in self.__clients.items():
                    try:
                        ch.Write(message.encode("UTF-8"))
                    except Exception:
                        pass
        except Exception as e:
            pass
        finally:
            print("AHIA, il client è morto e viene tolto dal dizionario")
            (ipClient, portClient) = self.__clientAddress
            self.__clients.pop((ipClient, portClient))