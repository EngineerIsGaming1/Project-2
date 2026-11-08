# Import socket module
from socket import *
import sys # In order to terminate the program

# import html mime to handle file extensions
import mimetypes

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)
serverSocket = socket(AF_INET, SOCK_STREAM)
# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
# "" just means localhost. Find the IP using command prompt ipconfig
serverSocket.bind(("", serverPort))

# Listen to at most 1 connection at a time
serverSocket.listen(1)

# Server should be up and running and listening to the incoming connections
while True:
    print('The server is ready to receive')

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()
    #print('Server connected to: ' + addr[0])

    # If an exception occurs during the execution of try clause
    # the rest of the clause is skipped
    # If the exception type matches the word after except
    # the except clause is executed
    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024).decode()

        # Extract the path of the requested object from the message
        # The path is the second part of HTTP header, identified by [1]
        filename = message.split()[1]
        print('Message is: \n' + filename)

        # use mimetypes to find out the filetype extension
        # guess_type outputs tuple (type, encoding). Only type is relevant here
        guessType, _ = mimetypes.guess_type(filename)
        # print(guessType)
        
        # If statement to return 404 not found if there's no file extension
        if guessType == None:
            # Send HTTP response message for file not found
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

             # Close the client connection socket
            connectionSocket.close()
            continue

        # open the file as raw bytes. r > read, b > bytes
        f = open(filename[1:], "rb")

        # Store the entire contenet of the requested file in a temporary buffer
        # Save the length of data to be used in html header later
        outputData = f.read()
        dataLength = len(outputData)

        # Send the HTTP response header line to the connection socket
        httpResponse = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: " + guessType + "\r\n"
            "Content-Length: " + str(dataLength) + "\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')

        # Send the content of the requested file to the connection socket
        # sendall needs bytes. If open() was used earlier without "rb" sendall would not work
        connectionSocket.sendall(httpResponse)
        connectionSocket.sendall(outputData)

        # Close the client connection socket
        print('Closing connection with: ' + addr[0])
        connectionSocket.close()    

    except IOError:
        # Send HTTP response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

        # Close the client connection socket
        connectionSocket.close()

serverSocket.close()
sys.exit() #Terminate the program after sending the corresponding data