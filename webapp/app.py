# to run
# go to directory that this file is in
# ifconfig | grep inet to find device ip
# python3 app.py
# http://ip:port/end/points
from flask import Flask
from flask import render_template

mywebapp = Flask(__name__)

@mywebapp.route('/')
def hello():
    return "Hello!"

@mywebapp.route('/service')
@mywebapp.route('/service/<service>')
def doservice(service=None):
    if (service == "washing"):
        triggered = 1
    if (service == "tv"):
        triggered = 2
    if (service == "coffee"):
        triggered = 3
    if (service == "lights"):
        triggered = 4
        # location =
    return render_template('service.html',service=service)
    #turn on tv

@mywebapp.route('/index')
def index():
    return "Hello World!"

if __name__ == '__main__':
    mywebapp.run(debug=True, host='0.0.0.0')
