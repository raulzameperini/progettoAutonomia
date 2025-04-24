import socket
import threading
from time import sleep


class MTClient:
    def __init__(self, UDPport):
        self.__serverIPAddress = None
        self.__serverPort = None
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.__UDPport = UDPport
        self.__localAddress = "0.0.0.0"
        self.__UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def Start(self):
       
        udpListenerThread = threading.Thread(target=self.__UDPListener, args=())
        udpListenerThread.start() 

        # Cerco di connettermi al server appena ho un indirizzo valido
        while True:
            if self.__serverIPAddress != None:
                connection = False
                try:
                    self.__TCPsocket.connect((self.__serverIPAddress, self.__serverPort))
                    print(f"Connessione al server {self.__serverIPAddress}:{self.__serverPort} riuscita!")
                    connection = True
                except Exception as e:
                    print(f"Errore: {str(e)}")

                if connection:
                    receiverThread = threading.Thread(target=self.__Receiver, args=())
                    receiverThread.start()        
                    senderThread = threading.Thread(target=self.__Sender, args=())
                    senderThread.start()

                    return  
                else:
                    print("Start: E' successo qualcosa di brutto...")
                    exit(1)
            else:
                sleep(5)


    def __Receiver(self):
        print("")
    def __Sender(self):
        print("")
    def __UDPListener(self):
        print("")