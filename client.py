import socket

# Server details
server_host = "localhost"
server_port = 8888

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))

try:
    # Get the string to check from the user
    sample_query = input("Enter the sample query: ") 

    # Send the request to the server with the correct file path and user-input string
    request = f"linuxpath=200k.txt&string={sample_query}"
    client_socket.sendall(request.encode())

    # Receive and print the server's response
    response = client_socket.recv(1024).decode()
    print(f"Server response: {response}")

finally:
    # Close the client socket
    client_socket.close()
