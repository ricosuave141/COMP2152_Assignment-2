"""
Author: Aaron Balayo | 101575606
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime


# TODO: Print Python version and OS name (Step iii)
print("Operating System:", platform.system())


# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
# Stores common port numbers mapped to their typical service names
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS"
}


# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value == "":
            raise ValueError("Target cannot be empty")
        self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")


# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)
# Using @property and setter allows controlled access to private variables.
# It ensures validation (like preventing empty targets) while keeping the attribute protected.
# This improves data integrity and encapsulation.


# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# PortScanner reuses code from NetworkTool through inheritance.
# It inherits the constructor and target handling logic.
# This avoids rewriting code and improves maintainability.


# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
#
# - scan_port(self, port):
#     Q4: What would happen without try-except here?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)
# Without try-except, any socket-related error could cause the program to crash.
# Issues like timeouts, unreachable hosts, or connection failures would stop the entire scan.
# Using try-except allows the program to handle errors gracefully and continue scanning other ports. This makes the scanner more robust and reliable.
#
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
#
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)
# Threading allows multiple ports to be scanned simultaneously rather than sequentially.
# This significantly reduces the total scanning time, especially when checking large ranges of ports.
# Without threading, each port would have to wait for the previous one to finish, making the process slow. Overall, threading improves efficiency and performance.
#
# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()

    def scan_port(self, port):
        # Q4 answer
        # Without try-except, any socket error would crash the program.
        # Errors like timeouts or unreachable hosts would stop execution.
        # Try-except allows scanning to continue safely.

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)

            result = s.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"

            service = common_ports.get(port, "Unknown")

            self.lock.acquire()
            self.scan_results.append((port, status, service))
            self.lock.release()

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")

        finally:
            s.close()

    def get_open_ports(self):
        return [r for r in self.scan_results if r[1] == "Open"]

    # Q2 answer
    # Threading allows multiple ports to be scanned at the same time.
    # This makes scanning much faster than doing it sequentially.
    # It improves efficiency for large port ranges.

    def scan_range(self, start_port, end_port):
        threads = []

        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()


# TODO: Create save_results(target, results) function (Step vii)
def save_results(target, results):
    conn = sqlite3.connect("scan_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            timestamp TEXT
        )
    """)

    for port, status, service in results:
        cursor.execute(
            "INSERT INTO scans VALUES (?, ?, ?, ?, ?)",
            (target, port, status, service, str(datetime.datetime.now()))
        )

    conn.commit()
    conn.close()


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scans")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        conn.close()

    except:
        print("No past scans found.")


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    pass
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."

    try:
        target = input("Enter target IP (default 127.0.0.1): ") or "127.0.0.1"
        start = int(input("Enter start port (1-1024): "))
        end = int(input("Enter end port (1-1024): "))

        if start < 1 or end > 1024 or start > end:
            print("Port must be between 1 and 1024.")
            exit()

    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        exit()

    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()

    scanner = PortScanner(target)

    print(f"Scanning {target} from port {start} to {end}...")
    scanner.scan_range(start, end)

    open_ports = scanner.get_open_ports()

    print("\nOpen Ports:")
    for port in open_ports:
        print(port)

    print(f"\nTotal open ports: {len(open_ports)}")

    save_results(target, scanner.scan_results)

    choice = input("Would you like to see past scan history? (yes/no): ").lower()
    if choice == "yes":
        load_past_scans()


# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Useful feature would be exporting results to a CSV file.
# This would allow users to easily open and analyze the data in spreadsheet software like Excel.
# It would also make it easier to share or store scan results for later use.