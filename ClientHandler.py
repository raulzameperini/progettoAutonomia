import threading, socket, pickle
import numpy as np

# Immagine bianca globale (100x100, RGB)
image = np.ones((100, 100, 3), dtype=np.uint8) * 255

global_mutex = threading.Lock()

class ClientHandler(threading.Thread):
    def __init__(self, clientSocket, clientAddress, clients):
        super().__init__()
        self.__clients = clients                      # Dizionario di tutti i client connessi
        self.__clientSocket = clientSocket            # Socket del client gestito da questo handler
        self.__clientAddress = clientAddress          # Indirizzo del client
                       # Mutex per la sincronizzazione sull'immagine

    def Write(self, message):
        # Invia un messaggio serializzato al client
        self.__clientSocket.sendall(message)

    def run(self):
        # Metodo principale del thread: gestisce la comunicazione con il client
        global image
        try:
            while True:
                data = self.__clientSocket.recv(1500) # Riceve dati dal client
                if not data:
                    break

                # pixel = (altezza, larghezza, [r, g, b])
                pixel = pickle.loads(data)            # Deserializza il pacchetto pixel
                y = int(pixel[0])                     # Altezza (riga)
                x = int(pixel[1])                     # Larghezza (colonna)
                colore = pixel[2]                     # Colore RGB

                with global_mutex:           # Modifica il pixel solo se le coordinate sono valide
                    if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                        
                        for x in range(dataLarghezza-1,dataLarghezza+1):
                            for y in range(dataAltezza-1,dataAltezza+1):
                                image[y, x] = colore
                                
                                
                        img_data = pickle.dumps(image)    # Serializza l'immagine aggiornata
                        # Invia l'immagine aggiornata a tutti i client connessi
                        for k, ch in self.__clients.items():
                            try:
                                ch.Write(img_data)
                            except Exception:
                                print("errore nell'invio dei dati al client")
        except Exception:
            print("errore generale client")
        finally:
            # Alla disconnessione, rimuove il client dal dizionario
            print("AHIA, il client è morto e viene tolto dal dizionario")
            (ipClient, portClient) = self.__clientAddress
            self.__clients.pop((ipClient, portClient))
