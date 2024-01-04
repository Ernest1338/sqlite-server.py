<h1><p align=center>sqlite-server.py</p></h1>
<h3><p align=center>Basic Sqlite Server Implementation + Client Library</p></h3>
<br \><br \>

# Server Usage
```bash
./server.py -h 0.0.0.0 -p 4567
```

# Example Client Usage
```Python
import sqlite

if __name__ == "__main__":
    # Connect to remote server
    db = sqlite.DB(host="localhost", port=4567, database="test", secret="secret")

    # Local database
    db = sqlite.DBLocal(filename="database.db")

    res, err = db.execute("SELECT * FROM users")
    print(res, err)

    db.close()
```

# License
### MIT

