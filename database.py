"""
    Database Class
"""

import sqlite3

class Database:
    def __init__(self, fileName):
        # Connect to the provided database
        self.con = sqlite3.connect(fileName, check_same_thread=False)
        self.db = self.con.cursor()

        # Create needed tables if they do not already exist
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS TimerEvents(
                Name TEXT,
                Time INTEGER,
                Dwell INTEGER,
                Enabled INTEGER,
                UNIQUE(name)
            )
        """)
        self.con.commit()
        # Create timer events
        self.createTimerEvent("GSE-1", -20, 80, True)
        self.createTimerEvent("GSE-2", -10, 70, False)
        self.createTimerEvent("TE-Ra", 10, 10, False)
        self.createTimerEvent("TE-Rb", 15, 5, False)
        self.createTimerEvent("TE-1", 10, 10, True)
        self.createTimerEvent("TE-2", 30, 10, False)
        self.createTimerEvent("TE-3", 30, 10, True)

    def close(self):
        self.con.close()

    def createTimerEvent(self, name, time, dwell, enabled):
        self.db.execute("INSERT OR IGNORE INTO TimerEvents(Name, Time, Dwell, Enabled) VALUES(?, ?, ?, ?)", [name, time, dwell, 1 if enabled else 0])
        self.con.commit()
    
    def updateTimerEvent(self, name, time, dwell, enabled):
        self.db.execute("UPDATE TimerEvents SET Time = ?, Dwell = ?, Enabled = ? WHERE Name = ?", [time, dwell, 1 if enabled else 0, name])
        self.con.commit()

    def getTimerEvent(self, name):
        result = self.db.execute("SELECT * FROM TimerEvents WHERE Name = ?", [name])
        self.con.commit()
        return result.fetchone()


    