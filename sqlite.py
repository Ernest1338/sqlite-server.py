import socket
import json
import sys

MAX_RESULT_SIZE = 131072


# TODO: prevent sql injection (sanitizer)


def exit2(m):
    print(m, file=sys.stderr)
    exit(1)


def db_guard(err):
    if err is not None:
        # print(err, file=sys.stderr)
        return True
    return False


class DB:
    def __init__(self, host, port, database, secret):
        self.host = host
        self.port = port
        self.database = database
        self.secret = secret

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))

        # Authentication
        self.connection.sendall((f"AUTH {secret}").encode("utf-8"))
        if self.connection.recv(128).decode("utf-8").strip() != "OK":
            exit2("ERROR: Authentication failed")

        # Database selection
        self.connection.sendall((f"DATABASE {database}").encode("utf-8"))
        if self.connection.recv(128).decode("utf-8").strip() != "OK":
            exit2("ERROR: Database selection failed")

    def execute(self, query):
        self.connection.sendall((f"{query}").encode("utf-8"))
        res = self.connection.recv(MAX_RESULT_SIZE).decode("utf-8")
        if res.split()[0] == "ERROR":
            return (None, res.strip())
        try:
            out = json.loads(res)
        except:
            out = None
        return (out, None)

    def execute_or_panic(self, query):
        res, err = self.execute(query)
        if db_guard(err):
            exit2("[ERROR] " + str(err))
        return res

    def rows_affected(self):
        res, err = self.execute("@ROWSAFFECTED")
        if db_guard(err):
            exit2("[ERROR] " + str(err))
        return res

    def close(self):
        self.connection.close()


class DBLocal:
    def __init__(self, filename="database.db"):
        import sqlite3

        self.filename = filename
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()

    def execute(self, query):
        import sqlite3

        try:
            res = self.cursor.execute(query).fetchall()
            if query.split()[0].upper() != "SELECT":
                self.db.commit()
        except sqlite3.Error as error:
            return (None, error)
        return (res, None)

    def execute_or_panic(self, query):
        res, err = self.execute(query)
        if db_guard(err):
            exit2("[ERROR] " + str(err))
        return res

    def rows_affected(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()
        self.db.close()
