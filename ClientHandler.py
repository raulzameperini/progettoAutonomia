import threading, socket, pickle
import numpy as np

# Immagine bianca globale (100x100, RGB)
image = np.ones((100, 100, 3), dtype=np.uint8) * 255

class ClientHandler(threading.Thread):
    def __init__(self, clientSocket, clientAddress, clients):
        super().__init__()
        self.__clients = clients
        self.__clientSocket = clientSocket
        self.__clientAddress = clientAddress
        self.__mutex = threading.Lock()

    def Write(self, message):
        self.__clientSocket.sendall(message)

    def run(self):
        global image
        try:
            while True:
                data = self.__clientSocket.recv(1500)
                if not data:
                    break

                # pixel = (altezza, larghezza, [r, g, b])
                pixel = pickle.loads(data)
                y = int(pixel[0])
                x = int(pixel[1])
                colore = pixel[2]

                with self.__mutex:
                    if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                        image[y, x] = colore
                        img_data = pickle.dumps(image)
                        for k, ch in self.__clients.items():
                            try:
                                ch.Write(img_data)
                            except Exception:
                                pass
        except Exception:
            pass
        finally:
            print("AHIA, il client è morto e viene tolto dal dizionario")
            (ipClient, portClient) = self.__clientAddress
            self.__clients.pop((ipClient, portClient))