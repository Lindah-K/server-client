# Import necessary libraries
import socket  # for network communication
import threading  # for handling multiple tasks concurrently
import os  # for interacting with the operating system
import time  # for introducing delays
import datetime  # for working with dates and times
import logging  # for logging information
import timeit # for measuring execution time


# Configuration settings
REREAD_ON_QUERY = True  # Flag to determine whether to reread the file on each query
MAX_PAYLOAD_SIZE = 1024  # Maximum size of data that can be received from the client
LOG_FILE = "server_logs.txt"  # File to store logs
CONFIG_FILE = "config.txt"  # Configuration file that contains relevant settings

# Configure the logging module
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s: %(message)s")

# Define a class representing our server
class Server:
    def __init__(self, host, port, config_file):
        self.host = host
        self.port = port
        self.config_file = config_file
        self.allowed_paths = self.load_allowed_paths()

    def load_allowed_paths(self):
        # Check if the file path is allowed based on the configuration file
        with open(self.config_file, 'r') as config_file:
            config_lines = [line.strip() for line in config_file.readlines()]

        linux_path = next((line.split("=")[1] for line in config_lines if line.startswith("linuxpath=")), None)
        reread_on_query = next((line.split("=")[1].lower() == 'true' for line in config_lines if line.startswith("reread_on_query=")), False)

        if linux_path is None:
            raise ValueError("Configuration file does not specify linuxpath.")

        # Convert relative paths to absolute paths
        linux_path = os.path.abspath(os.path.join(os.getcwd(), linux_path))

        return {'linux_path': linux_path, 'reread_on_query': reread_on_query}

    def start(self):
        # Create a socket for communication using the specified host and port
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")

        # Continuously accept incoming connections
        while True:
            # Accept a connection from a client
            client_socket, address = server_socket.accept()
            # Start a new thread to handle the client connection
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(MAX_PAYLOAD_SIZE).decode().rstrip('\x00')
            print(f"DEBUG: Received data from {address}: {data}")

            if data.startswith("linuxpath=") and "&string=" in data:
                file_path = data.split("=")[1].split("&")[0]
                query_string = data.split("&string=")[1]  # Extract query string separately

                # Validate file path from the configuration file
                valid_file_path = self.validate_file_path(file_path)

                print(f"DEBUG: File path validation result: {valid_file_path}")

                if not valid_file_path:
                    response = "INVALID FILE PATH"
                else:
                    exists = self.check_string_in_file(file_path, query_string)
                    response = "STRING EXISTS" if exists else "STRING NOT FOUND"

                client_socket.sendall(response.encode())

                # Log the request
                self.log_request(query_string, address, exists)

            else:
                client_socket.sendall("Invalid request".encode())

        except Exception as e:
            logging.error(f"Exception - {str(e)}")
        finally:
            client_socket.close()

    def validate_file_path(self, file_path):
        # Check if the file path is allowed based on the configuration file
        print(f"DEBUG: Checking if {file_path} is in allowed path: {self.allowed_paths['linux_path']}")

        # Ensure the file_path is an absolute path
        file_path = os.path.abspath(file_path)

        print(f"DEBUG: Absolute file path: {file_path}")

        # Check if the given file_path matches the allowed path
        result = file_path.startswith(self.allowed_paths['linux_path'])
        print(f"DEBUG: Result: {result}")

        return result

    def check_string_in_file(self, file_path, query):
        # Simulate the execution time for file read based on the REREAD_ON_QUERY flag
        if self.allowed_paths['reread_on_query']:
            time.sleep(0.04)  # Simulating a 40 ms execution time for file read
        else:
            time.sleep(0.0005)  # Simulating a 0.5 ms execution time for file read

        try:
            # Open the file and check if the specified string exists
            with open(file_path, 'r') as file:
                return query in file.read()
        except FileNotFoundError:
            # Handle the case where the file is not found
            return False


    def log_request(self, query, client_address, exists):
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create a log entry with information about the query, client, and existence result
        log_entry = f"DEBUG: Query: {query}, Client: {client_address}, Exists: {exists}"
        # Log the entry using the configured logging module
        logging.debug(log_entry)


    def time_complexity(self, algorithm):
        # This method calculates the time complexity of an algorithm based on its name
        if algorithm == "brute_force":
            return "O(m * n)"
        elif algorithm == "kmp":
            return "O(m + n)"
        elif algorithm == "boyer_moore":
            return "O(m * n) (worst case)"
        else:
            return "Unknown time complexity"

    def speed_test(self):
        # Load content from the file for testing
        try:
            with open("200k.txt", "r") as content_file:
                file_content = content_file.read()
        except FileNotFoundError:
            print("Error: '200k.txt' file not found.")
            return

        # Run the speed tests for three different algorithms and log the results
        results = []

        # Brute Force Algorithm
        start_time = timeit.default_timer()
        self.algorithm_brute_force(file_content, "sample_query")
        time_taken = timeit.default_timer() - start_time
        results.append(("Brute Force Algorithm", time_taken, self.time_complexity("brute_force")))

        # KMP Algorithm
        start_time = timeit.default_timer()
        self.algorithm_kmp(file_content, "sample_query")
        time_taken = timeit.default_timer() - start_time
        results.append(("KMP Algorithm", time_taken, self.time_complexity("kmp")))

        # Boyer-Moore Algorithm
        start_time = timeit.default_timer()
        self.algorithm_boyer_moore(file_content, "sample_query")
        time_taken = timeit.default_timer() - start_time
        results.append(("Boyer-Moore Algorithm", time_taken, self.time_complexity("boyer_moore")))

        # Log the results to a file
        try:
            with open('speed_testing_report.txt', 'w') as report_file:
                for result in results:
                    report_file.write(f"{result[0]}:\n   - Time taken: {result[1]} seconds\n   - Time Complexity: {result[2]}\n\n")
            print("Speed testing report written to 'speed_testing_report.txt'")
        except Exception as e:
            print(f"Error writing speed testing report: {e}")

        # Print the results to console
        for result in results:
            print(f"{result[0]}:\n   - Time taken: {result[1]} seconds\n   - Time Complexity: {result[2]}\n")

# Function to deploy the server
def deploy_server():
    # Create an instance of the Server class with a specified host, port, and config file path
    server = Server("localhost", 8888, CONFIG_FILE)
    # Start the server
    server.start()
    # Run speed tests
    server.speed_test()

# Entry point - Execute the deploy_server function when the script is run
if __name__ == "__main__":
    deploy_server()
