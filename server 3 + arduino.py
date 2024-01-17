import socket
import select
import serial

SERVER = "192.168.1.58"
PORT = 5050
ADDR = (SERVER, PORT)
FORMATO = "utf-8"
HEADER = 64
TIMEOUT = 2
INDIRIZZO_NAO = "192.168.70.104"       #indirizzo del NAO che è costante

conn_nao = None                 #oggetto di connessione dedicato al NAO

SERIAL_PORT = "/dev/ttyACM0"   #porta seriale per ingresso arduino

arduino = serial.Serial(
	port = SERIAL_PORT,
	baudrate=9600,
	timeout=1
    
)
arduino.reset_input_buffer()


def ricevi_comandi(conn):
    connesso = True

    while connesso:             #fin quando il NAO è connesso

        if arduino.in_waiting > 0:      #se ci sono ingresso nella variabile arduino
            try:
                line = arduino.readline().decode(FORMATO)               #decode e leggo la mia linea
                print(line)                                     #gliela stampo 
            except UnicodeDecodeError:
                print("ERRORE")                             #se nun legge nulla
                
        readers, _, _, = select.select([conn], [], [], TIMEOUT)   #controlla se ci sono connessioni dalle quali è possibile leggere dati
        if readers:
            lunghezza_msg = conn.recv(HEADER).decode(FORMATO) 
            if lunghezza_msg:
                lunghezza_msg = int(lunghezza_msg)                  #righe 20-23 controllo della lunghezza del messaggio arrivato
                msg = conn.recv(lunghezza_msg).decode(FORMATO) 

            match msg:                          #controlla, per ogni caso, il tipo di messaggio da mandare al client
                case "ESC":
                    print("Sto chiudendo la connessione al server...")
                    connesso = False

                case _:                                     #caso default, ovvero quando non c'è nessun messaggio particolare, 
                    print(f"Messaggio arrivato: {msg}")     #esegue ciò che c'è scritto sotto
                    risposta = "Messaggio ricevuto"
                    conn.send(risposta.encode(FORMATO))
                    print(risposta)

        else:                                   #si collega alla prima condizione (readers)
            check = "Si è staccato il NAO?"     #se rileva connessioni dalle quali può ricevere dati ma NON RICEVE DATI,
            conn.send(check.encode(FORMATO))    #il server manderà uno spam di messaggi "Si è staccato il NAO?" fin quando non riceverà un messaggio
            print(check)                        #in pratica, il concetto di event-loop

    conn.close()


def inizializza_server(conn_nao, backlog = 1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #righe 47-50: inizializzazione del server e ammissione delle connessioni
        s.bind(ADDR)
        print("Server in ascolto...")
        s.listen(backlog)
    
    except socket.error as errore:
        print(f"Server error \n{errore}")
        inizializza_server(backlog = 1)

    while True:
        conn, indirizzo_client = s.accept()     #accetta connessioni all'infinito fin quando non si connette il NAO
        print(f"Connesso {indirizzo_client}")

        if indirizzo_client[0] == INDIRIZZO_NAO:
            conn_nao = conn
            print("Si è connesso il NAO!")          #quando si connette il NAO, verrà inizializzata la variabile conn_nao e
            ricevi_comandi(conn_nao)                #viene eseguita la funzione che riceve i comandi
        else:
            conn.close()
            break

    s.close()
    

if __name__ == "__main__":
    inizializza_server(conn_nao, backlog = 1)