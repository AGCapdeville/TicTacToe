import argparse, socket, logging, threading
import engine

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):
    def __init__(self, address, socket, ttt, player, turn):
        threading.Thread.__init__(self)
        self.csock = socket
        self.ttt = ttt
        self.player = player
        self.turn = turn
        logging.info('New connection added.')


    def run(self):
        # game phase: turn by turn, as long as game isn't over.
        while self.ttt.is_game_over() is '-':
            # with our condtional lock
            with self.turn:
                # as long as it isn't our turn....
                while self.ttt.whos_turn() != self.player:
                    self.turn.wait() # wait

                
                # SEND: board
                self.csock.sendall( ('BOR'+self.ttt.get_board()+'\n').encode() )
                msg = self.recv_until(self.csock, b'\n').decode('utf-8')
                logging.info('Board:'+msg)

                if self.ttt.is_game_over() is '-':

                    # SEND: Player Icon & Available Moves
                    self.csock.sendall( ('TRN' + self.player + self.ttt.get_available_moves() + '\n').encode() )

                    # RECEIVED: Move:
                    move = self.recv_until(self.csock, b"\n").decode('utf-8')
                    print("\n TURN: " + str(self.ttt.turns) + ", POS:" + move)
                    #TODO: Add Checking for move:
                    self.ttt.make_move(int(move[0]))
                    self.ttt.display_board()                    
                    
                    # SEND: Updated Board
                    self.csock.sendall( ('BOR'+self.ttt.get_board()+'\n').encode() )
                    msg = self.recv_until(self.csock, b'\n').decode('utf-8')
                    logging.info('Board:'+msg)
                    # !~ might be an issue if I don't wait here for a confirmation that the client recv the board...

                    # update board:
                    # self.csock.sendall( ('END' + board + '\n').encode() )                
                    self.turn.notify()
                
        # disconnect client
        print("\n victor: "+self.ttt.is_game_over()+"\n")
        self.csock.sendall( ('SCR'+self.ttt.is_game_over()+'\n').encode() )

        self.csock.close()
        logging.info('Server Closing...')


    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data

    def recv_until(self, sock, suffix):
        """Receive bytes over socket `sock` until we receive the `suffix`."""
        message = sock.recv(4096)
        if not message:
            raise EOFError('socket closed')
        while not message.endswith(suffix):
            data = sock.recv(4096)
            if not data:
                raise IOError('received {!r} then socket closed'.format(message))
            message += data
        return message


def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))


    ttt = engine.TicTacToeEngine() # single instance of our engine
    turn = threading.Condition() # conditional lock
    player = 'X'

    ttt.display_board()
    
    maxPlayers = 2
    players = 0

    while True:
        sock.listen(2)
        logging.info('Server is listening on port ' + str(port))
        # client has connected
        sc,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc, ttt, player, turn)
        t.start()
        
        if player == 'X':
            player = 'O'
        else:
            player = 'X'
        players += 1
        if players == maxPlayers:
            break
        

