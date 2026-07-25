import mysql.connector 
import os 
from  dotenv import load_dotenv

load_dotenv()

PASSWORD=os.getenv("MYSQL_ROOT_PASSWORD")
DATABASE=os.getenv("MYSQL_DATABASE")
HOST=os.getenv("MYSQL_HOST")
PORT=os.getenv("MYSQL_PORT")



ARGS={
    'user':'root',
    'password':PASSWORD,
    'host':HOST,
    'port':PORT,
    'database':DATABASE 
}

class Database():
    
    def __init__(self):
        self.ARGS=ARGS
        
    def fetch_query(self, query , params):
        self.query=query
        self.params=params
        with mysql.connector.connect(**self.ARGS) as db :
            with db.cursor() as cursor:
                cursor.execute(self.query,self.params)
                return cursor.fetchall()
                
                
    def execute_query(self, query, params):
        self.query=query 
        self.params=params
        with mysql.connector.connect(**self.ARGS) as db :
            with db.cursor() as cursor:
                cursor.execute(self.query, self.params)
                db.commit()
                
                
