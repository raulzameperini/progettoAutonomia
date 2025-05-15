import socket
import ClientHandler
import threading
import psutil 
from time import sleep

# Classe principale del server
class Server:
    def __init__(self, TCPport, UDPport):
        # Imposta l'indirizzo IP su tutte le interfacce disponibili
        self.__ipAddress = "0.0.0.0"
        # Porta TCP su cui il server ascolta
        self.__TCPport = TCPport
        # Porta UDP per il broadcasting
        self.__UDPport = UDPport
        # Crea il socket TCP
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Dizionario per tenere traccia dei clien t connessi
        self.__clients = {}

    # Avvia il server
    def Start(self):
        connection = False
        try:
            # Effettua il bind del socket TCP e inizia ad ascoltare
            self.__TCPsocket.bind((self.__ipAddress, self.__TCPport))
            self.__TCPsocket.listen(10)
            connection = True
            print(f"Server in ascolto su {self.__ipAddress}:{self.__TCPport}...")
        except Exception as e:
            print(f"Qualcosa è andato storto nell'avvio del server: {str(e)}")

        if connection:
            # Avvia un thread per il broadcasting UDP
            broadcastingUDP_Thread = threading.Thread(target=self.__BroadcastingUDP, args=())
            broadcastingUDP_Thread.start()

            # Ciclo principale: accetta nuove connessioni TCP
            while True:
                try:
                    (clientSocket, clientAddress) = self.__TCPsocket.accept()
                    # Crea un gestore per il nuovo client
                    client = ClientHandler.ClientHandler(clientSocket, clientAddress, self.__clients)
                    (ipClient, portClient) = clientAddress
                    # Aggiunge il client al dizionario dei client connessi
                    self.__clients[(ipClient, portClient)] = client
                    # Avvia il thread del client handler
                    client.start()
                except Exception as e:
                    pass  # Ignora eventuali errori nell'accettare connessioni
        
    # Metodo privato per il broadcasting UDP della porta TCP
    def __BroadcastingUDP(self):
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        message = f"{self.__TCPport}"
        while True:
            # Per ogni interfaccia di rete attiva
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    # Solo indirizzi IPv4 non di loopback
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        # Invia il messaggio in broadcast sulla rete
                        udpSocket.sendto(message.encode("utf-8"), (addr.broadcast, self.__UDPport))
                        sleep(1)  # Attende 5 secondi prima di ripetere
                
    