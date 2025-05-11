from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv("../../")

class Database:
    def __init__(self):
        self.host = "localhost"
        self.database = os.getenv("MARIADB_DATABASE")
        self.root_password = os.getenv("MARIADB_ROOT_PASSWORD")
        self.port = int(os.getenv("MARIADB_PORT"))
        self.connect = mysql.connector.connect(user='root', password=self.root_password, host=self.host, database=self.database, port=self.port)
        self.cursor = self.connect.cursor()
    
    def query(self, sql, params=None, fetchone=False, fetchall=False):
        try:
            self.cursor.execute(sql, params)

            if fetchone:
                res = self.cursor.fetchone()
            elif fetchall:
                res = self.cursor.fetchall()
            else:
                self.connect.commit()
                res = True
            
            return res
        except mysql.connector.Error as e :
            print(f"[DB ERROR] {e}")
            return False