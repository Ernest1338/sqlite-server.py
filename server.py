#!/bin/python3

import threading
import socket
import sqlite3
import json
import sys

AUTH_KEY = "secret"


def handle_client(con):
    authenticated = False
    current_database = None
    db_cursor = None

    while True:
        try:
            data = con.recv(4096)
        except:
            break
        if not data:
            break

        data = data.decode("utf-8").strip()

        parsed = data.split()
        if len(parsed) == 0:
            con.sendall(b"ERROR 11: empty command\n")
            continue

        # Handle authentication
        if not authenticated:
            if parsed[0] != "AUTH":
                con.sendall(b"ERROR 21: authentication needed\n")
                continue

            if len(parsed) != 2:
                con.sendall(b"ERROR 22: incorrect AUTH command usage\n")
                continue

            user_key = parsed[1]

            if user_key != AUTH_KEY:
                con.sendall(b"ERROR 23: wrong auth key\n")
                continue

            authenticated = True

            con.sendall(b"OK\n")
            continue

        # Now we are authenticated

        # Handle selecting current database
        if current_database is None:
            if parsed[0] != "DATABASE":
                con.sendall(b"ERROR 31: current database not selected\n")
                continue

            if len(parsed) != 2:
                con.sendall(b"ERROR 32: incorrect DATABASE command usage\n")
                continue

            database = parsed[1]

            current_database = sqlite3.connect(database + ".db")
            db_cursor = current_database.cursor()

            con.sendall(b"OK\n")
            continue

        try:
            if data == "@ROWSAFFECTED":
                con.sendall((str(db_cursor.rowcount) + "\n").encode("utf-8"))
                continue

            res = db_cursor.execute(data)

            if data.split()[0].upper() == "SELECT":
                out = json.dumps(res.fetchall())
                con.sendall((out + "\n").encode("utf-8"))
            else:
                current_database.commit()
                con.sendall(b"OK\n")
            continue

        except sqlite3.Error as error:
            con.sendall((f"ERROR {error}\n").encode("utf-8"))
            pass

    if current_database is not None:
        current_database.close()
    con.close()


def print_help():
    print(
        f"""Usage: {sys.argv[0]} [options]

Options:
    --host, -h\t\tBind address\t\t(default: 0.0.0.0)
    --port, -p\t\tBind port\t\t(default: 4567)
    --secret, -s\tAuthentication secret\t(default: secret)
    --help\t\tPrint this help screen"""
    )
    exit(0)


def main():
    global AUTH_KEY

    host = "0.0.0.0"
    port = 4567

    if "--help" in sys.argv:
        print_help()

    if "--host" in sys.argv:
        host = sys.argv[sys.argv.index("--host") + 1]
    if "-h" in sys.argv:
        host = sys.argv[sys.argv.index("-h") + 1]

    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    if "-p" in sys.argv:
        port = int(sys.argv[sys.argv.index("-p") + 1])

    if "--secret" in sys.argv:
        AUTH_KEY = sys.argv[sys.argv.index("--secret") + 1]
    if "-s" in sys.argv:
        AUTH_KEY = sys.argv[sys.argv.index("-s") + 1]

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to a specific address and port
    sock.bind((host, port))
    print(f"Binding server on: {host}:{port}")

    # Listen for incoming connections (max 5)
    sock.listen(5)

    while True:
        # Wait for a connection
        connection, client_address = sock.accept()

        # Create a new thread for each connection
        client_thread = threading.Thread(target=handle_client, args=(connection,))
        client_thread.start()


if __name__ == "__main__":
    main()
