from Server import Server

if __name__ == "__main__":
    server = Server(TCPport=12345, UDPport=54321)  # Scegli le porte che preferisci
    server.Start()


