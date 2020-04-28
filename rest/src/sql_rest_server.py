from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
import json
import time
from datetime import datetime
import mysql.connector as mysql
import os

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']

def signup(req):
  firstname = req.params.getall("firstname")[0]
  lastname = req.params.getall("lastname")[0]
  email = req.params.getall("email")[0]
  assert isinstance(firstname, str)
  assert isinstance(lastname, str)
  assert isinstance(email, str)

  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  cursor.execute("""
    SELECT COUNT(id) FROM Users 
    WHERE email='%s';
    """ % email
  )
  records = cursor.fetchall()

  # check if the email already exists
  if records[0][0] != 0:
    print("ERROR: email already signed up")
    return Response('ERROR')
  else:
    cursor.execute("""
        INSERT INTO Users (firstname, lastname, email) 
        VALUES ('%s', '%s', '%s');
      """ % (firstname, lastname, email))
    db.commit()
    print("SIGN UP SUCCESS!")

  return Response('SUCCESS')


if __name__ == '__main__':
  config = Configurator()

  config.add_route('signup', '/signup')
  config.add_view(signup, route_name='signup')

  app = config.make_wsgi_app()
  server = make_server('0.0.0.0', 5000, app)
  server.serve_forever()
