from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from pyramid.session import SignedCookieSessionFactory
from pyramid.response import Response
from datetime import datetime
import json
import time
import requests
import mysql.connector as mysql
import os

# REST_SERVER = os.environ['REST_SERVER'] #REST_SERVER is found in the docker-compose.yml file
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']

def get_home(req):
  if 'user' in req.session:
    return render_to_response('templates/login.html', {'user':req.session['user']})
  else:
    return HTTPFound(req.route_url("get_login"))

def get_login(req):
  error = req.session.pop_flash('login_error')
  error = error[0] if error else ''
  return render_to_response('templates/landing.html', {'error': error})

def post_login(req):
  email = None
  password = None
  if req.method == "POST":
    email = req.params['email']
    password = req.params['password']

  # Connect to the database and try to retrieve the user
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  query = "SELECT email, password FROM Users WHERE email='%s';" % email
  cursor.execute(query)
  user = cursor.fetchone() # will return a tuple (email, password) if user is found and None otherwise
  db.close()

  # If user is found and the password is valid, store in session, and redirect to the homepage
  # Otherwise, redirect back to the login page with a flash message
  # Note: passwords should be hashed and encrypted in actual production solutions!
  if user is not None and user[1] == password:
    req.session['user'] = user[0] # set the session variable
    return HTTPFound(req.route_url("get_home"))
  else:
    req.session.invalidate() # clear session
    req.session.flash('Invalid login attempt. Please try again.', 'login_error')
    return HTTPFound(req.route_url("get_login"))

def signUp(req):
  #get username and password using the name of the corresponding field
  firstname = req.params.getall("fname")[0]
  lastname = req.params.getall("lname")[0]
  email = req.params.getall("email")[0]
  password = req.params.getall("pw")[0]
  print(firstname)
  print(lastname)
  print(email)
  print(password)
  # assert isinstance(firstname, str)
  # assert isinstance(lastname, str)
  # assert isinstance(email, str)
  # assert isinstance(password, str)

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
    return render_to_response('templates/landing.html', {'books': "a"}, request=req)
  else:
    cursor.execute("""
        INSERT INTO Users (firstname, lastname, email, password) 
      """ % (firstname, lastname, email, password))
    db.commit()
    return render_to_response('templates/landing.html', {'books': "a"}, request=req)

def getUsers(req):
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  cursor.execute("SELECT COUNT(*) FROM Users;")
  records = cursor.fetchall()
  return {'count': records[0][0]}

def getNews(req):
  db = mysql.connect(host=db_host, database=db_name, user=db_user, passwd=db_pass)
  cursor = db.cursor()
  cursor.execute("SELECT * FROM News ORDER by id desc;")
  records = cursor.fetchall()
  return records


if __name__ == '__main__':
  config = Configurator()

  config.include('pyramid_jinja2')
  config.add_jinja2_renderer('.html')

  config.add_route('get_login', '/')
  config.add_view(get_login, route_name='get_login')

  config.add_route('post_login', '/post_login')
  config.add_view(post_login, route_name='post_login')

  config.add_route('get_home', '/home')
  config.add_view(get_home, route_name='get_home')

  # Add a route to the home page - login page - using the endpoint: /signup
  config.add_route('v3', '/signup')
  config.add_view(signUp, route_name='v3')

  config.add_route('v4', '/getUsers')
  config.add_view(getUsers, route_name='v4', renderer='json', request_method='GET')

  config.add_route('v5', '/getNews')
  config.add_view(getNews, route_name='v5', renderer='json', request_method='GET')

  # Path for static resources
  config.add_static_view(name='/', path='./templates', cache_max_age=3600)

  # Create the session using a signed
  session_factory = SignedCookieSessionFactory(os.environ['SESSION_SECRET_KEY'])
  config.set_session_factory(session_factory)

  app = config.make_wsgi_app()
  server = make_server('0.0.0.0', 5000, app)
  server.serve_forever()

# def start(req):
#   return render_to_response('templates/landing.html', {'books': "a"}, request=req)

# def signUp(req):
#   #get username and password using the name of the corresponding field
#   firstname = req.params.getall("fname")
#   lastname = req.params.getall("lname")
#   email = req.params.getall("email")
#   password = req.params.getall("pw")
#   data = {"firstname": firstname, "lastname": lastname, "email": email, "password": password}

#   #Send a request to the rest_server via a post method and access content returned as text (using .text)
#   signup_response = requests.post(REST_SERVER + "/signup", data=data).text
#   print('signup response: ', signup_response)

#   if signup_response == "true":
#     return render_to_response('templates/landing.html', {'books': "a"}, request=req)
#   else:
#     return render_to_response('templates/landing.html', {'books': "a"}, request=req)

# def getUsers(req):
#   get_user_response = requests.get(REST_SERVER + "/getUsers").json()
#   print('get_user_response: ', get_user_response)

#   return get_user_response

# def getNews(req):
#   get_news_response = requests.get(REST_SERVER + "/getNews").json()
#   print('get_news_response: ', get_news_response)

#   return get_news_response


# if __name__ == '__main__':
#   config = Configurator()

#   config.include('pyramid_jinja2')
#   config.add_jinja2_renderer('.html')

#   # Add a route to the home page using the endpoint: /
#   config.add_route('v1', '/')
#   config.add_view(start, route_name='v1')

#   #Add a route to the home page - login page - using the endpoint: /signup
#   config.add_route('v3', '/signup')
#   config.add_view(signUp, route_name='v3')

#   config.add_route('v4', '/getUsers')
#   config.add_view(getUsers, route_name='v4', renderer='json', request_method='GET')

#   config.add_route('v5', '/getNews')
#   config.add_view(getNews, route_name='v5', renderer='json', request_method='GET')

#   config.add_static_view(name='/', path='./templates', cache_max_age=3600) #expose the public folder for the CSS file

#   app = config.make_wsgi_app()
#   server = make_server('0.0.0.0', 5000, app)
#   server.serve_forever()
