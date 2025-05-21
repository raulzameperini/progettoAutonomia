
import threading, pickle      # Importa moduli per thread e serializzazione(conversione oggetti in sequenza di byte) import numpy as np                    # Importa numpy per manipolare l'immagine come matrice (array multidimensionale)
import numpy as np            # Importa numpy per usare  l'immagine come matrice (array multidimensionale)

# Crea un'immagine bianca globale di 100x100 pixel, 3 sonno i canali RGB(255,255,255) e imposta il tipo di dato a unsigned int 8 bit
image = np.ones((100, 100, 3), dtype=np.uint8) * 255
# Mutex  per evitare che più thread modifichino contemporaneamente l'immagine 
# è glovale perchè deve essere condivisa tra più thread
global_mutex = threading.Lock()      

class ClientHandler(threading.Thread):
    def __init__(self, clientSocket, clientAddress, clients):
        super().__init__()              # Inizializza il thread
        self.__clients = clients                      # Dizionario di tutti i client connessi
        self.__clientSocket = clientSocket            # Socket del client gestito da questo handler
        self.__clientAddress = clientAddress          # Indirizzo del client
                     

    def Write(self, message):
        # Invia i byte del messaggio serializzato al client
        self.__clientSocket.sendall(message)

    def run(self):
        # Metodo principale del thread: gestisce la comunicazione con il client
        global image # deve essere global oerchè va condivisa tra tutti i client connessi al server
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
                blocco_altezza = int(pixel[3])
                blocco_larghezza = int(pixel[4])

                with global_mutex:           # Modifica il pixel solo se le coordinate sono valide
                    if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                        
                        for dy in range(blocco_altezza):
                            for dx in range(blocco_larghezza):
                                ny = y + dy
                                nx = x + dx
                                if 0 <= ny < image.shape[0] and 0 <= nx < image.shape[1]:
                                    image[ny, nx] = colore
                                
                                
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
