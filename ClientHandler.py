import threading, socket, pickle
from PIL import Image


class ClientHandler(threading.Thread):
    def __init__(self, clientSocket, clientAddress, clients):
        
        self.__clients = clients
        self.__clientSocket = clientSocket
        self.__clientAddress = clientAddress

        self.__mutex = threading.Lock()

    def Write(self, message):
        self.__clientSocket.sendall(message)

    def run(self):
        global image, mutex
        try:
            
            while True:
                data = self.__clientSocket.recv(1500)
                if not data:
                    break

                # Decodifica i dati ricevuti: pixel = (x, y, [r, g, b])
                pixel = pickle.loads(data)

                with self.__mutex:
                    image[pixel[1], pixel[0]] = pixel[2]  # Modifica il pixel  riga prima di colonna
                    img_data = pickle.dumps(image)  # Serializza l'immagine aggiornata
                    self.__clientSocket.send(img_data)  # Invia l'immagine a tutti i client connessi
                    

                
                
                
                
                for k, ch in self.__clients.items():
                    try:
                        ch.Write(img_data)
                    except Exception:
                        pass
        except Exception as e:
            pass
        finally:
            print("AHIA, il client è morto e viene tolto dal dizionario")
            (ipClient, portClient) = self.__clientAddress
            self.__clients.pop((ipClient, portClient))