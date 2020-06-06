# Import MySQL Connector Driver
import mysql.connector as mysql

# Load the credentials from the secured .env file
import os
from dotenv import load_dotenv
load_dotenv('credentials.env')
from datetime import datetime

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST'] # different than inside the container and assumes default port of 3306

# Connect to the database
db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
cursor = db.cursor()

# DELETE THIS LINE
cursor.execute("drop table if exists Users;")

# Create tables (Users, Moves)
try:
    cursor.execute("""
      CREATE TABLE Users (
        id integer  AUTO_INCREMENT PRIMARY KEY,
        firstname   VARCHAR(30) NOT NULL,
        lastname    VARCHAR(30) NOT NULL,
        email       VARCHAR(30) NOT NULL,
        password    VARCHAR(30) NOT NULL,
        created_at  TIMESTAMP
      );
    """)
    print("Users table created")
except:
  print("Users table already exists")

cursor.execute("show tables;")
result = cursor.fetchall()
print(result)

# Insert Records
query = "insert into Users (firstname, lastname, email, password, created_at) values (%s, %s, %s, %s, %s)"
values = ('po', 'huang', 'phh003@ucsd.edu', 'abc123', datetime.now())
cursor.executemany(query, values)
db.commit()

# Selecting Records
print('---------- DATABASE INITIALIZED ----------')
cursor.execute("SELECT * from Users;")
[print(x) for x in cursor]

db.close()
