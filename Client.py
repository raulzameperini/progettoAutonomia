import socket, pickle
from PIL import Image
import threading
from time import sleep


class Client:
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
        try:
            while True:
                # Attendo una risposta dal server
                receivedData = self.__TCPsocket.recv(65536)  

                if receivedData:
                    image = pickle.loads(receivedData) # Deserializza l'immagine
                    img = Image.fromarray(image) # Converte da array NumPy a immagine PIL
                    img.show() # Mostra l'immagine 
                if not receivedData:
                    print("Il server non risponde più:/")
                    break

        except Exception:
            print("__Receiver: E' successo qualcosa di brutto...")
            exit(1)
    def __Sender(self):
        try:
            while True:
                print("Specifica l'altezza del pixel")
                dataAltezza = str(input(""))
                print("Specifica la larghezza del pixel")
                dataLarghezza = str(input(""))
                print("Specifica un colore, esempio:([255,0,0])")
                dataColore = str(input(""))

                pixel = (dataAltezza, dataLarghezza, dataColore) #Crear il pacchetto di modifica

                self.__TCPsocket.send(pixel)
                self.__TCPsocket.close()
                

        except Exception:
            print("__Sender: E' successo qualcosa di brutto...")
            exit(1)

    def __UDPListener(self):
        print(f"Attesa di un volantino dal server...")
        # chiedo al SO di poter associare il mio processo ad una porta
        try:
            # chiedo al SO la porta
            self.__UDPsocket.bind((self.__localAddress, self.__UDPport))            
        except Exception as e:
            # Probabilmente la porta è occupata da un altro processo
            print(f"Probabilmente la porta UDP è occupata da un altro processo...")
            print(f"ERRORE: {str(e)}")
            exit(1)
        
        # Per semplicità attendo UN SOLO messaggio UDP 

        # Attesa di un messaggio dal server (max 1500 bytes)
        (data, address) = self.__UDPsocket.recvfrom(1500)
        receivedData = data.decode("utf-8")
        print(f"\nRicevuto: {address}:{receivedData}")
        # Salvo i valori
        # Mi serve solo l'indirizzo IP del server, che si trova sull'header pacchetto UDP
        (self.__serverIpAddress, _) = address
        # La porta di ascolto del server si trova all'interno del pacchetto UDP
        self.__serverPort = int(receivedData)

        self.__UDPsocket.close()