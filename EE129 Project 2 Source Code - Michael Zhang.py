# Import socket module
from socket import *
import sys # In order to terminate the program

# import html mime to handle file extensions
import mimetypes

# import threading to handle server and console commands at the same time
import threading

# create global variable active used for the while loop managing the server
active = True

# notFound() function. Takes a socket as input and sends a 404 not found http response using that socket.
def notFound(inputSocket):
    # Send HTTP response message for file not found
    inputSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    inputSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

    # Close the client connection socket
    inputSocket.close()
    return

# receieveMessage function. Takes http response, separates the request type and URL from the header, then analyzes the body.
# returns "filename", the name and extension of the content requested by http
# and "filetype", which is needed in the http response header to handle the transmitted file
def receiveMessage(inputMessage):
    # Extract the path of the requested object from the message
    # The path is the second part of HTTP header, identified by [1]
    socketMessage = inputMessage.split()[1]
    messageType = inputMessage.split()[0]

    # if the request type is "POST", checks is posted username and password are valid using Accounts.txt. 
    # Responds with Granted/Denied pages depending on credentials and increments counter of attempts
    if messageType == "POST":
        userAccess = "Denied"
        messageBody = inputMessage.split("\r\n\r\n", 1)[1]

        accountsFile = open("Accounts.txt")
        successFile = open("Successes.txt")
        failFile = open("Fails.txt")

        # iterate through the lines of Accounts.txt for the valid username and password combinations
        for i in accountsFile:
            if messageBody == i.split("\n")[0]:
                userAccess = "Granted"

        if userAccess == "Granted":
            fileName = "login_success.html"
            fileType, _ = mimetypes.guess_type("login_success.html")
            successNumber = int(successFile.read()) + 1
            successFile = open("Successes.txt", "w")
            successFile.write(str(successNumber))
        else:
            fileName = "login_failed.html"
            fileType, _ = mimetypes.guess_type("login_failed.html")
            failNumber = int(failFile.read()) + 1
            failFile = open("Fails.txt", "w")
            failFile.write(str(failNumber))

    # if the request type is "GET", analyzes the URL for an empty "/" message and "green" and "red" keywords
    # returns the base, green and red webpages respectively as dictated by project requirements
    elif messageType == "GET":
        if socketMessage == "/":
            fileName = "base.html"
            fileType, _ = mimetypes.guess_type("base.html")
        elif "green" in  socketMessage:
            fileName = "green.html"
            fileType, _ = mimetypes.guess_type("green.html")
        elif "red" in socketMessage:
            fileName = "red.html"
            fileType, _ = mimetypes.guess_type("red.html")
        else:
            # use mimetypes to find out the filetype extension
            # guess_type outputs tuple (type, encoding). Only "type" is relevant here
            fileType, _ = mimetypes.guess_type(socketMessage)
            fileName = socketMessage[1:]

    return (fileName, fileType)

# commandPrompt function. Takes string input from command prompt for manual server manipulation
# "close" closes the socket given to commandPrompt through its arguements, 
# then sets the global "active" variable to False, which disables the main server loop
# "help" gives the user a guide on how to close the server
# any other input will result in a "not recognized" message
def commandPrompt(inputSocket):
    global active

    while active:
        try:
            commandMessage = input()
            if commandMessage == "close":
                inputSocket.close()
                active = False
            elif commandMessage == "help":
                print("input 'close': Close active sockets and exit program\n")
            else:
                print("command not recognized. Type 'help' for all commands\n")
        except EOFError:
            print("Keyboard interrupt detected. Closing server")
            inputSocket.close()
            active = False
        

# Main server function. Runs a while loop using global variable "active"
# Once a connection request is received, create a dedicated connection socket and handle http requests using receiveMessage function
# After analyzing http request, opens and reads raw bytes of requested content, 
# then replies with HTTP 200 response header followed by requested content
def startServer():
    global active

    while active:
        print('The server is ready to receive')

        # If an exception occurs during the execution of try clause
        # the rest of the clause is skipped
        # If the exception type matches the word after except
        # the except clause is executed
        try:
            # Set up a new connection from the client
            connectionSocket, addr = serverSocket.accept()
            
            # Receives the request message from the client
            message = connectionSocket.recv(1024).decode()
            fileName, guessType = receiveMessage(message)
            # print(fileName + str(guessType) + "\n")
            
            # If statement to return 404 not found if there's no file extension
            if guessType == None:
                # print("Not found \n")
                notFound(connectionSocket)
                continue

            # open the file as raw bytes. r > read, b > bytes
            f = open(fileName, "rb")

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
            # print('Closing connection with: ' + addr[0])
            connectionSocket.close()    

        # exceptions to handle manual interrupt of server activity. 
        except IOError:
            if active == True:
                notFound(connectionSocket)
            else:
                print("Server socket closed")


# main function begins here

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

# Create 2 threads that run in parallel. One for the main server loop, and another to analyze user input through the command prompt
thread1 = threading.Thread(target=commandPrompt, args=(serverSocket,), daemon=True)
thread2 = threading.Thread(target=startServer)

# Start both threads
thread1.start()
thread2.start()

# Exit program when terminated
sys.exit()