import socket
import sys
import time
import os
import struct

print ("\nBienvenido al servidor FTP.\n\nPara empezar, conecta un cliente.")

TCP_IP = "127.0.0.1" 
TCP_PORT = 1456 
BUFFER_SIZE = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Esperando a que el cliente se conecte...")
conn, addr = s.accept()
print ("\nConectado a por dirección: {}".format(addr))

def upld():
    conn.send("1".encode())
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_size).decode()
    conn.send("1".encode())
    file_size = struct.unpack("i", conn.recv(4))[0]
    start_time = time.time()
    output_file = open(file_name, "wb")
    bytes_recieved = 0
    print ("\nRecibiendo...")
    while bytes_recieved < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_recieved += BUFFER_SIZE
    output_file.close()
    print ("\nArchivo recibido {}".format(file_name))
    conn.send(struct.pack("f", time.time() - start_time))
    conn.send(struct.pack("i", file_size))
    return

def list_files():
    print ("Listando de archivos...")
    files = os.listdir(os.getcwd())
    conn.send(struct.pack("i", len(files)))
    total_directory_size = 0
    for file in files:
        file_path = os.path.join(os.getcwd(), file)
        conn.send(struct.pack("i", len(file)))
        conn.send(file.encode())
        conn.send(struct.pack("i", os.path.getsize(file_path)))
        total_directory_size += os.path.getsize(file_path)
        conn.recv(BUFFER_SIZE)
    conn.send(struct.pack("i", total_directory_size))
    conn.recv(BUFFER_SIZE)
    print ("Listado de archivos enviados con éxito.")
    return

def dwld():
    conn.send("1".encode())
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    print (file_name_length)
    file_name = conn.recv(file_name_length).decode()
    print (file_name)
    if os.path.isfile(file_name):
        conn.send(struct.pack("i", os.path.getsize(file_name)))
    else:
        print ("Nombre de archivo no válido")
        conn.send(struct.pack("i", -1))
        return
    conn.recv(BUFFER_SIZE)
    start_time = time.time()
    print ("Enviando archivo...")
    content = open(file_name, "rb")
    l = content.read(BUFFER_SIZE)
    while l:
        conn.send("1".encode())
        l = content.read(BUFFER_SIZE)
    content.close()
    conn.recv(BUFFER_SIZE)
    conn.send(struct.pack("f", time.time() - start_time))
    return


def delf():
    conn.send("1".encode())
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length).decode()
    print("Archivo:", file_name)
    if os.path.isfile(file_name):
        conn.send(struct.pack("i", 1))
    else:
        conn.send(struct.pack("i", -1))
    confirm_delete = conn.recv(BUFFER_SIZE).decode()
    if confirm_delete == "Y":
        try:
            os.remove(file_name)
            conn.send(struct.pack("i", 1))
        except:
            print ("Error al eliminar {}".format(file_name))
            conn.send(struct.pack("i", -1))
    else:
        print ("Eliminar abandonado por el cliente")
        return

def quit():
    conn.send("1".encode())
    conn.close()
    s.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

while True:
    print ("\n\nEsperando instrucciones...")
    data = conn.recv(BUFFER_SIZE)
    data = data.decode()
    print ("\nInstrucción recibida: {}".format(data))
    if data == "UPLD":
        upld()
    elif data == "LIST":
        list_files()
    elif data == "DWLD":
        dwld()
    elif data == "DELF":
        delf()
    elif data == "QUIT":
        quit()
    data = None