import socket
import threading
import psutil
from time import sleep
import ClientHandler

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
    
