import socket
import selectors
import types

"""The server will accept multi connection client"""
host = 'localhost'
port = 54321
sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('The server is listening on ', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('Accepted connection from: ', addr)
    sock.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #     register socket to selectors
    sel.register(conn, events, data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask and selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to ', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask and selectors.EVENT_WRITE:
        if data.outb:
            print('echoing ', repr(data.outb), ' to ', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
