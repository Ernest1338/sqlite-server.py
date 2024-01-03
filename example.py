import sqlite

if __name__ == "__main__":
    # Connect to remote server
    db = sqlite.DB(host="localhost", port=4567, database="test", secret="secret")

    # Local database
    db = sqlite.DBLocal(filename="database.db")

    res, err = db.execute("SELECT * FROM users")
    print(res, err)

    db.close()
