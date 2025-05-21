# Documentazione Progetto Secondo Quadrimestre
### Teoria sulla quale si basa il progetto:
Socket
Programmazione ad oggetti
Multithreading
TCP-UDP
mutua esclusione

### Socket:
I socket sono un'interfaccia di programmazione che consente la comunicazione tra due nodi di una rete. Possono essere visti come "porte" attraverso le quali i processi inviano e ricevono dati.
Nel progetto si utilizzano socket TCP e socket UDP:
TCP (Transmission Control Protocol): garantisce una comunicazione affidabile e ordinata. Inoltre è orientato alla connessione: prima di trasmettere dati, viene stabilita una connessione tra le parti.
UDP (User Datagram Protocol): è un protocollo non orientato alla connessione, più veloce ma meno affidabile rispetto al TCP. I pacchetti possono arrivare fuori ordine o andare persi.


### Programmazione ad oggetti:
La programmazione ad oggetti  è un metodo di programmazione che organizza il codice attorno a oggetti, che rappresentano entità del mondo reale o concetti astratti. Ogni oggetto combina dati (detti attributi) e comportamenti (cioè metodi, o funzioni associate).

Principi chiave:
Classe: Un modello che descrive un tipo di oggetto, definisce gli attributi e i metodi
Incapsulamento: ogni oggetto mantiene il proprio stato interno nascosto.
Ereditarietà: le classi possono derivare da altre, estendendo il comportamento.

Utilizzo nel progetto
Nel progetto, la OOP viene utilizzata per modellare entità come client, server, thread di gestione, messaggi, e risorse condivise. Ogni entità ha responsabilità ben definite.

### Multithreading:
Il multithreading consente l’esecuzione concorrente di più thread all’interno di un unico processo. È utile per mantenere reattivo il sistema, per esempio gestendo più client simultaneamente.
Vantaggi:
Concorrenza e parallelismo (dove supportato).

Gestione efficiente di operazioni bloccanti (come la ricezione dati da socket).

Utilizzo nel progetto
Ogni connessione client può essere gestita da un thread separato. Oppure si possono avere thread dedicati alla ricezione, elaborazione, e risposta. Questo aumenta la scalabilità del server.

### TCP e UDP:
Come già accennato nella sezione Socket, TCP e UDP sono due protocolli della suite Internet con caratteristiche distinte.





### MUTUA ESCLUSIONE:
La mutua esclusione è un principio fondamentale della programmazione concorrente. Serve per garantire che solo un thread per volta possa accedere a una risorsa condivisa (come una struttura dati o un file).
Come funziona:
Lock/Mutex: blocchi esclusivi.

Semafori: contatori sincronizzati.

Monitor/Synchronized: costrutti linguistici per sezioni critiche.


Utilizzo nel progetto
Quando più thread interagiscono con dati condivisi (es. lista utenti, file di log, stato del server), la mutua esclusione previene condizioni di race e inconsistenza dei dati.

### OBIETTIVO DEL PROGETTO:
Il progetto consiste nella realizzazione di un programma basato su architettura client-server che consente a più client di modificare in tempo reale un'immagine condivisa. I client possono inviare coordinate e colore di un pixel da modificare, e il server aggiorna l'immagine globale inviandone una versione aggiornata a tutti i client connessi.

### ARCHITETTURA DEL PROGETTO:
L’architettura implementata è una classica Client-Server, con:
Server centrale che gestisce lo stato condiviso (l’immagine modificabile).


Client multipli che si connettono al server e possono modificare l’immagine, ricevendone in tempo reale gli aggiornamenti.


### COSA AVVIENE QUANDO SI AVVIA IL PROGETTO?
Server in ascolto (TCP e UDP):
Il server apre una socket TCP sulla porta specificata (es. 12345).

In parallelo, avvia un thread che invia ciclicamente un broadcast UDP per informare i client su quale porta TCP ascolta.

Client in attesa (UDP):
Il client apre una socket UDP sulla porta 54321 in ascolto.

Quando riceve il messaggio broadcast dal server, salva:
L’IP del server (preso dal pacchetto UDP ricevuto).
La porta TCP (contenuta nel messaggio UDP).
A questo punto, prova a connettersi via TCP al server.

Connessione TCP avvenuta:
Una volta connesso via TCP, il client avvia:
Un thread ricevente: riceve l’immagine aggiornata.
Un thread mittente: invia coordinate dei pixel e il colore.

Invio modifiche dal client al server (TCP):
Il client chiede all’utente:
Coordinata x, y del pixel da modificare.
Colore in formato esadecimale.
Invia un pacchetto pickle al server con:
 (y, x, [r, g, b]).


Elaborazione lato server:
Il server riceve il pacchetto e modifica immagine in quella posizione.
Poi invia l’intera immagine aggiornata (di nuovo via pickle) a tutti i client connessi.

Visualizzazione dell’immagine:
Ogni client che riceve l’immagine aggiornata:
Deserializza l’immagine con pickle.
La converte in PIL.Image e la mostra a schermo con .show().
