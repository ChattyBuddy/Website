from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.renderers import render_to_response

import requests
import os

REST_SERVER = os.environ['REST_SERVER'] #REST_SERVER is found in the docker-compose.yml file

def start(req):
  return render_to_response('templates/landing.html', {'books': "a"}, request=req)

def signUp(req):
  #get username and password using the name of the corresponding field
  firstname = req.params.getall("fname")
  lastname = req.params.getall("lname")
  email = req.params.getall("email")
  data = {"firstname": firstname, "lastname": lastname, "email": email}

  #Send a request to the rest_server via a post method and access content returned as text (using .text)
  signup_response = requests.post(REST_SERVER + "/signup", data=data).text
  print('signup response: ', signup_response)

  if signup_response == "true":
    return render_to_response('templates/landing.html', {'books': "a"}, request=req)
  else:
    return render_to_response('templates/landing.html', {'books': "a"}, request=req)


if __name__ == '__main__':
  config = Configurator()

  config.include('pyramid_jinja2')
  config.add_jinja2_renderer('.html')

  # Add a route to the home page using the endpoint: /
  config.add_route('v1', '/')
  config.add_view(start, route_name='v1')

  #Add a route to the home page - login page - using the endpoint: /signup
  config.add_route('v3', '/signup')
  config.add_view(signUp, route_name='v3')

  config.add_static_view(name='/', path='./templates', cache_max_age=3600) #expose the public folder for the CSS file

  app = config.make_wsgi_app()
  server = make_server('0.0.0.0', 5000, app)
  server.serve_forever()
