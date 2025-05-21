import socket
import ClientHandler
import threading
import psutil 
from time import sleep

# Classe principale del server
class Server:
    def __init__(self, TCPport, UDPport):
        self.__ipAddress = "0.0.0.0"                 # Ascolta su tutte le interfacce
        self.__TCPport = TCPport                     # Porta TCP per i client
        self.__UDPport = UDPport                     # Porta UDP per il broadcast
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket TCP
        self.__clients = {}                          # Dizionario dei client connessi

    def Start(self):
        # Avvia il server TCP e il thread di broadcast UDP
        connection = False
        try:
            self.__TCPsocket.bind((self.__ipAddress, self.__TCPport))
            self.__TCPsocket.listen(10)
            connection = True
            print(f"Server in ascolto su {self.__ipAddress}:{self.__TCPport}...")
        except Exception as e:
            print(f"Qualcosa è andato storto nell'avvio del server: {str(e)}")

        if connection:
            # Avvia il thread per il broadcast UDP
            broadcastingUDP_Thread = threading.Thread(target=self.__BroadcastingUDP, args=())
            broadcastingUDP_Thread.start()

            # Ciclo principale: accetta nuove connessioni TCP
            while True:
                try:
                    (clientSocket, clientAddress) = self.__TCPsocket.accept()
                    # Crea un handler per il nuovo client
                    client = ClientHandler.ClientHandler(clientSocket, clientAddress, self.__clients)
                    (ipClient, portClient) = clientAddress
                    self.__clients[(ipClient, portClient)] = client
                    client.start() # Avvia il thread del client handler
                except Exception as e:
                    pass  # Ignora eventuali errori nell'accettare connessioni
        
    def __BroadcastingUDP(self):
        # Invia periodicamente la porta TCP tramite UDP broadcast su tutte le interfacce
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        message = f"{self.__TCPport}"
        while True:
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                            broadcast_ip = addr.broadcast or "255.255.255.255"
                            try:
                                udpSocket.sendto(message.encode("utf-8"), (broadcast_ip, self.__UDPport))
                                print(f"[BROADCAST] Inviato a {broadcast_ip}:{self.__UDPport}")
                            except Exception as e:
                                print(f"[ERRORE] Invio fallito su {broadcast_ip}: {e}")
                sleep(5)
            except Exception as e:
                print(f"[ERRORE] Ciclo broadcast interrotto: {e}")
                break
