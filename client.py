import argparse, socket, logging

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)


def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data

def recv_until(sock, suffix):
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


def client(host,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))


    while True:
        print('Waiting for turn...\n')
        msg = recv_until(sock, b'\n').decode('utf-8')

        if msg.startswith('BOR'):
            board = msg[3:len(msg)]
            print('\n'+board)
            sock.sendall( ('RCVD\n').encode() )
        
        if msg.startswith('TRN'):
            playerIcon = msg[3]
            aMoves = msg[4:len(msg)]
            logging.info('Available Moves: ')
            logging.info('Positions: ' + aMoves)
            logging.info('Your Turn Player: ' + playerIcon)
            
            while True:
                move = input("Pos: ")
                if move in msg:
                    break
                else:
                    logging.info('INVALID MOVE')
            sock.sendall( (move + '\n' ).encode())


        if msg.startswith('TIE'):
            logging.info('The game is a tie')
        
        if msg.startswith('SCR'):
            logging.info('Player '+ msg[3] +' WON')
            break
    
    print('exiting...')
    sock.close()



if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Tic Tac Oh No Client (TCP edition)')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)