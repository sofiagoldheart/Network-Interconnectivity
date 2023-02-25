import socket
import sys
import os
import struct

TCP_IP = "127.0.0.1"  
TCP_PORT = 1456  
BUFFER_SIZE = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conn():
  print("Enviando solicitud de servidor...")
  try:
    s.connect((TCP_IP, TCP_PORT))
    print("Conexión exitosa")
  except:
    print("Conexión fallida. Asegúrese de que el servidor esté en línea.")

def upld(file_name):
  print("\nSubiendo archivo: {}...".format(file_name))
  try:
    content = open(file_name, "rb")
  except:
    print("No se pudo abrir el archivo. Asegúrese de que el nombre del archivo se haya ingresado correctamente.")
    return
  try:
    s.send(b"UPLD")
  except:
    print("No se pudo realizar la solicitud del servidor. Asegúrese de que se haya establecido una conexión.")
    return
  try:
    s.recv(BUFFER_SIZE)
    s.send(struct.pack("h", sys.getsizeof(file_name)))
    s.send(file_name.encode())
    s.recv(BUFFER_SIZE)
    s.send(struct.pack("i", os.path.getsize(file_name)))
  except:
    print("Error al enviar los detalles del archivo.")
  try:
    l = content.read(BUFFER_SIZE)
    print("\nEnviando...")
    while l:
      s.send(l)
      l = content.read(BUFFER_SIZE)
    content.close()
    upload_time = struct.unpack("f", s.recv(4))[0]
    upload_size = struct.unpack("i", s.recv(4))[0]
    print("\nArchivo enviado: {}\nTiempo transcurrido: {}s\nTamaño del archivo: {}b".format(
      file_name, upload_time, upload_size))
  except:
    print("Error al enviar el archivo")
    return
  return

def list_files():
  print("Solicitando archivos...\n")
  try:
      s.send("LIST".encode())
      number_of_files = struct.unpack("i", s.recv(4))[0]
      for i in range(number_of_files):
          file_name_size = struct.unpack("i", s.recv(4))[0]
          file_name = s.recv(file_name_size)
          file_size = struct.unpack("i", s.recv(4))[0]
          print("\t{} - {}b".format(file_name.decode(), file_size))
          s.send(b"1") 
  except:
    return
  try:
      total_directory_size = struct.unpack("i", s.recv(4))[0]
      print("Tamaño total del directorio: {}b".format(total_directory_size))
      s.send(b"1")
      return
  except:
      print("No se pudo recuperar el listado.")
      return
    
def dwld(file_name):
    print ("Descargando archivo: {}".format(file_name))
    try:
        s.send("DWLD".encode())
    except:
        print ("No se pudo realizar la solicitud del servidor. Asegúrese de que se haya establecido una conexión.")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", len(file_name.encode())))
        s.send(file_name.encode())
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print ("El archivo no existe. Asegúrese de que el nombre se haya ingresado correctamente.")
            return
    except:
        print ("Error al comprobar el archivo")
    try:
        s.send("1".encode())
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print ("\nDownloading...")
        while bytes_recieved < file_size:
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print ("Descargado correctamente{}".format(file_name))
        s.send("1".encode())
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print ("Tiempo transcurrido: {}s\nTamaño del archivo: {}b".format(time_elapsed, file_size))
    except:
        print ("Error al descargar el archivo.")
        return
    return

def delf(file_name):
    print ("Eliminando archivo: {}...".format(file_name))
    try:
        s.send("DELF".encode())
        s.recv(BUFFER_SIZE)
    except:
        print("No se pudo conectar al servidor, asegurese que una conexión fue establecida.")
        return
    try:
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name.encode())  
    except:
        return     
    existence = struct.unpack("i", s.recv(4))[0]
    if existence == -1:
        print("El archivo no existe")
        return
    try:
        print("Eliminar: ", file_name)
        borrar_opt = input("(Y/N): ").upper()
    except:
        return     
    if borrar_opt == "Y":
        s.send("Y".encode())
        borrado = struct.unpack("i", s.recv(4))[0]
        if borrado == 1:
            print("Archivo eliminado correctamente.")
            return
        else:
            print("Archivo no eliminado.")
            return
    else:
        s.send("N".encode())
        return

def quit():
    s.send("QUIT".encode())
    s.recv(BUFFER_SIZE)
    s.close()
    print ("Conexión finalizada")
    return

print("\n\nBienvenido(a) al cliente FTP, para comenzar suba el archivo registrando su dirección con el primer comando:\nUPLD file_path : Subir archivo\nLIST           : Listar archivos\nDWLD file_path : Descargar archivo\nDELF file_path : Eliminar archivo\nQUIT           : Salir")

while True:
    prompt = input("\nIngrese un comando: ")
    if prompt[:4].upper() == "UPLD":
        conn()
        upld(prompt[5:])
    elif prompt[:4].upper() == "LIST":
        list_files()
    elif prompt[:4].upper() == "DWLD":
        dwld(prompt[5:])
    elif prompt[:4].upper() == "DELF":
        delf(prompt[5:])
    elif prompt[:4].upper() == "QUIT":
        quit()