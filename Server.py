import socket                      # Serve per la comunicazione di rete (internet o rete locale)
import ClientHandler               # Importa il modulo che gestisce i singoli client
import threading                   # Serve per eseguire più cose contemporaneamente (thread)
import psutil                      # Serve per ottenere informazioni sulle interfacce di rete del computer
from time import sleep             # Serve per mettere in pausa il programma per alcuni secondi

# Questa è la classe principale che rappresenta il server
class Server:
    def __init__(self, TCPport, UDPport):
        # Quando crei un oggetto Server, queste sono le sue "caratteristiche"
        self.__ipAddress = "0.0.0.0"                 # "0.0.0.0" vuol dire: ascolta su tutte le connessioni di rete disponibili
        self.__TCPport = TCPport                     # Porta TCP su cui i client si collegheranno
        self.__UDPport = UDPport                     # Porta UDP su cui il server invierà il messaggio broadcast
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea una "presa" TCP per accettare connessioni
        self.__clients = {}                          # Un dizionario per tenere traccia di tutti i client collegati

    def Start(self):
        # Questo metodo avvia il server vero e proprio
        connection = False
        try:
            # Prova a "collegare" la presa TCP a tutte le interfacce e alla porta scelta
            self.__TCPsocket.bind((self.__ipAddress, self.__TCPport))
            self.__TCPsocket.listen(10)  # Si mette in ascolto, pronto ad accettare fino a 10 connessioni in coda
            connection = True
            print(f"Server in ascolto su {self.__ipAddress}:{self.__TCPport}...")
        except Exception as e:
            # Se qualcosa va storto, stampa l'errore
            print(f"Qualcosa è andato storto nell'avvio del server: {str(e)}")

        if connection:
            # Se la connessione è andata a buon fine, parte un thread che invia periodicamente il messaggio UDP broadcast
            broadcastingUDP_Thread = threading.Thread(target=self.__BroadcastingUDP, args=())
            broadcastingUDP_Thread.start()

            # Questo ciclo accetta continuamente nuovi client che si collegano via TCP
            while True:
                try:
                    (clientSocket, clientAddress) = self.__TCPsocket.accept()  # Accetta una nuova connessione
                    # Crea un oggetto che gestirà questo client (in un thread separato)
                    client = ClientHandler.ClientHandler(clientSocket, clientAddress, self.__clients)
                    (ipClient, portClient) = clientAddress
                    self.__clients[(ipClient, portClient)] = client  # Salva il client nel dizionario
                    client.start() # Avvia il thread che gestisce il client
                except Exception as e:
                    pass  # Se c'è un errore nell'accettare un client, lo ignora e continua

    def __BroadcastingUDP(self):
        # Questo metodo invia ogni 5 secondi un messaggio UDP broadcast con la porta TCP del server
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Crea una presa UDP
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1) # Imposta la presa per il broadcast
        message = f"{self.__TCPport}"  # Il messaggio è semplicemente la porta TCP del server
        while True:
            try:
                # Per ogni interfaccia di rete del computer 
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        # Se è un indirizzo IPv4 e non è locale (127.0.0.1)
                        if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                            broadcast_ip = addr.broadcast or "255.255.255.255"  # Prende l'indirizzo broadcast
                            try:
                                # Invia il messaggio UDP a quell'indirizzo broadcast e alla porta UDP scelta
                                udpSocket.sendto(message.encode("utf-8"), (broadcast_ip, self.__UDPport))
                                print(f"[BROADCAST] Inviato a {broadcast_ip}:{self.__UDPport}")
                            except Exception as e:
                                print(f"[ERRORE] Invio fallito su {broadcast_ip}: {e}")
                sleep(5)  # Aspetta 5 secondi prima di inviare di nuovo
            except Exception as e:
                print(f"[ERRORE] Ciclo broadcast interrotto: {e}")
                break  # Se c'è un errore grave, esce dal ciclo

