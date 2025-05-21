import socket, pickle                # Importa i moduli per la comunicazione di rete e la serializzazione
from PIL import Image                # Importa la libreria PIL per la gestione delle immagini
import threading                     # Importa il modulo per la gestione dei thread
from time import sleep# Importa la funzione sleep per le attese temporali
import matplotlib.pyplot as plt

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
        # Thread che riceve immagini dal server
        try:
            while True:
                # Attende una risposta dal server (immagine serializzata)
                receivedData = self.__TCPsocket.recv(65536)  

                if receivedData:
                    image = pickle.loads(receivedData) # Deserializza l'immagine (array NumPy)
                    print("Ricevuta immagine:", image.shape)
    
                    plt.imshow(image)
                    plt.axis('off')
                    plt.show()
                    # img = Image.fromarray(image)       # Converte da array NumPy a immagine PIL
                    # img.show() # Mostra l'immagine
                    # img.save("debug_image.png")
                    # sleep(2) 
                if not receivedData:
                    print("Il server non risponde più:/")
                    break

        except Exception:
            print("__Receiver: E' successo qualcosa di brutto...")
            exit(1)

    def __Sender(self):
        # Thread che invia le modifiche dei pixel al server
        try:
            while True:            
                print("Specifica l'altezza del pixel")
                dataAltezza = str(input(""))
                print("Specifica la larghezza del pixel")
                dataLarghezza = str(input(""))
                print("Specifica un colore in formato esadecimale, esempio: #FF0000")
                dataColore = input("").strip()

                # Controllo e conversione colore esadecimale
                if dataColore.startswith("#") and len(dataColore) == 7:
                    try:
                        r = int(dataColore[1:3], 16)
                        g = int(dataColore[3:5], 16)
                        b = int(dataColore[5:7], 16)
                        coloreRGB = [r, g, b]
                    except ValueError:
                        print("Formato colore non valido. Riprova.")
                        continue
                else:
                    print("Formato colore non valido. Riprova.")
                    continue

                pixel = (dataAltezza, dataLarghezza, coloreRGB)  # Crea il pacchetto di modifica

                self.__TCPsocket.send(pickle.dumps(pixel))       # Serializza e invia il pacchetto al server
                #self.__TCPsocket.close()                         # Chiude la connessione TCP dopo l'invio (probabilmente da correggere)
        except Exception:
            print("__Sender: E' successo qualcosa di brutto...")
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
        # Salva l'indirizzo IP del server (dal pacchetto UDP)
        (self.__serverIPAddress, _) = address
        # Salva la porta TCP del server (dal contenuto del pacchetto UDP)
        self.__serverPort = int(receivedData)

        self.__UDPsocket.close()  # Chiude la socket UDP dopo aver ricevuto il messaggio