import socket, pickle                # Importa i moduli per la comunicazione di rete e la serializzazione
from PIL import Image                # Importa la libreria PIL per la gestione delle immagini
import threading                     # Importa il modulo per la gestione dei thread
from time import sleep               # Importa la funzione sleep per le attese 


class Client:
    def __init__(self, UDPport):
        # Inizializza le variabili di istanza
        self.__serverIPAddress = None            # Indirizzo IP del server (verrà ricevuto via UDP)
        self.__serverPort = None                 # Porta TCP del server (verrà ricevuta via UDP)
        self.__TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP per la comunicazione principale
        
        self.__UDPport = UDPport                 # Porta UDP su cui il client ascolta
        self.__localAddress = "0.0.0.0"          # Indirizzo locale (tutte le interfacce)
        self.__UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # Socket UDP per ricevere il "volantino" dal server

    def Start(self):
        # Avvia il thread che ascolta i messaggi UDP dal server
        udpListenerThread = threading.Thread(target=self.__UDPListener, args=())
        udpListenerThread.start() 

        # Ciclo infinito: attende di ricevere l'indirizzo IP del server via UDP
        while True:
            if self.__serverIPAddress != None:
                connection = False
                try:
                    # Prova a connettersi al server tramite TCP
                    self.__TCPsocket.connect((self.__serverIPAddress, self.__serverPort))
                    print(f"Connessione al server {self.__serverIPAddress}:{self.__serverPort} riuscita!")
                    connection = True
                except Exception as e:
                    print(f"Errore: {str(e)}")

                if connection:
                    # Se la connessione è riuscita, avvia i thread per ricevere e inviare dati
                    receiverThread = threading.Thread(target=self.__Receiver, args=())
                    receiverThread.start()        
                    senderThread = threading.Thread(target=self.__Sender, args=())
                    senderThread.start()

                    return  # Esce dal metodo Start
                else:
                    print("Start: E' successo qualcosa di brutto...")
                    exit(1)
            else:
                # Se non ha ancora ricevuto l'indirizzo IP, attende 5 secondi e riprova
                sleep(5)

    def __Receiver(self):
        # Thread che riceve immagini dal server e le mostra 
        try:
            while True:
                # Attende una risposta dal server (immagine serializzata)
                receivedData = self.__TCPsocket.recv(65536)  

                if receivedData:
                    # Deserializza l'immagine ricevuta (array NumPy)
                    image = pickle.loads(receivedData) 
                    print("Ricevuta immagine")
                    # Converte l'array NumPy in una immagine PIL e la mostra
                    img = Image.fromarray(image) 
                    img.show()
                    # Aspetta 2 secondi per evitare sovrapposizioni rapide
                    sleep(2) 
                if not receivedData:
                    # Se il server ha chiuso la connessione
                    print("Il server non risponde più:/")
                    break

        except Exception:
            print("__Receiver: E' successo qualcosa di brutto...")
            exit(1)

    def __Sender(self):
        # Thread che invia le modifiche dei pixel al server
        try:
            while True:
                # Funzione interna per controllare se è un intero 
                def leggi_intero(messaggio):
                    while True:
                        valore = input(messaggio).strip() #Chiede all'utente un input e rimuovere eventuali spazi 
                        if valore.isdigit():  # Controlla se il valore inserito è composto solo da cifre ( un numero intero positivo)
                            return int(valore)
                        else:
                            print("Inserisci un numero valido.")            
                x= leggi_intero("Scrivi la coordinata x del pixel (colonna):")
                y = leggi_intero("Scrivi la coordinata  Y del pixel (riga): ")

                # per verificare che le coordinate siano nei limiti 0–100 dell'immagine
                if not (0 <= x <= 100 and 0 <= y <= 100):
                    print("Coordinate fuori dai limiti. Inserisci valori tra 0 e 99.")
                    continue
                print("Specifica un colore in formato esadecimale, esempio: #FF0000")
                dataColore = input("").strip()
                blocco_larghezza = leggi_intero("Inserisci la larghezza del blocco da colorare:")
                blocco_altezza = leggi_intero("Inserisci l'altezza del blocco da colorare:")
                # Controllo e conversione colore esadecimale
                if dataColore.startswith("#") and len(dataColore) == 7:
                    try:
                        r = int(dataColore[1:3], 16)
                        g = int(dataColore[3:5], 16)
                        b = int(dataColore[5:7], 16)
                        coloreRGB = [r, g, b]
                    except ValueError:
                        print("Formato colore non valido. Riprova.")
                        continue #Riparte da capo con il codice
                else:
                    print("Formato colore non valido. Riprova.")
                    continue
                
                
                pixel = (x, y, coloreRGB, blocco_altezza, blocco_larghezza)  #  Crea pacchetto con coordinate, colore e dimensione del blocco

                self.__TCPsocket.send(pickle.dumps(pixel))       # Serializza e invia il pacchetto al server via TCP

        except Exception as e:
            print(f"__Sender: E' successo qualcosa di brutto... {e}" )
            exit(1)
    
    

    def __UDPListener(self):
        # Thread che ascolta il "volantino" UDP dal server per scoprire IP e porta TCP
        print(f"Attesa di un volantino dal server...")
        try:
            # Associa la socket UDP alla porta locale specificata
            self.__UDPsocket.bind((self.__localAddress, self.__UDPport))            
        except Exception as e:
            # Se la porta è già occupata, stampa errore ed esce
            print(f"Probabilmente la porta UDP è occupata da un altro processo...")
            print(f"ERRORE: {str(e)}")
            exit(1)
        
        # Attende un solo messaggio UDP dal server (max 1500 bytes)
        (data, address) = self.__UDPsocket.recvfrom(1500)
        receivedData = data.decode("utf-8")
        print(f"\nRicevuto: {address}:{receivedData}")
        # Salva l'indirizzo IP del server dal pacchetto UDP
        (self.__serverIPAddress, _) = address
        # Salva la porta TCP del server dal contenuto del pacchetto UDP
        self.__serverPort = int(receivedData)

        self.__UDPsocket.close()  # Chiude la socket UDP dopo aver ricevuto il messaggio