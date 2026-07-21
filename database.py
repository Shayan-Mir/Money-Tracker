import mysql.connector 
import os 
from  dotenv import load_dotenv

load_dotenv()

PASSWORD=os.getenv("MYSQL_ROOT_PASSWORD")
db=mysql.connector.connect(user='root', password=PASSWORD,host='127.0.0.1',port= '3306',database='my_money_bot')

cursor=db.cursor()



cursor.close()
db.close()