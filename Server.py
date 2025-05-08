import socket
import ClientHandler
import threading
import psutil 
from time import sleep



class Sever:
    def __init__(self, TCPport, UDPport):
        self.__ipAddress = "0.0.0.0"
        self.__TCPport = TCPport
        self.__UDPport = UDPport
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = {}

    def Start(self):
        connection = False
        try:
            self.__TCPsocket.bind((self.__ipAddress, self.__TCPport))
            self.__TCPsocket.listen(10)
            connection = True
        except Exception as e:
            print(f"Qualcosa è andato storto nell'avvio del server: {str(e)}")

        if connection:
            broadcastingUDP_Thread = threading.Thread(target=self.__BroadcastingUDP, args=())
            broadcastingUDP_Thread.start()

            while True:
                try:
                    (clientSocket, clientAddress) = self.__TCPsocket.accept()
                    client = ClientHandler.ClientHandler(clientSocket, clientAddress, self.__clients)
                    (ipClient, portClient) = clientAddress
                    self.__clients[(ipClient, portClient)] = client
                    client.start()
                except Exception as e:
                    pass
        
    def __BroadcastingUDP(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        message = f"{self.__TCPport}"
        while True:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        udpSocket.sendto(message.encode("utf-8"), (addr.broadcast, self.__UDPport))
                        sleep(5) 
                
                
    
