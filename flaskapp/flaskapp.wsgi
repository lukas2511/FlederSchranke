#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/customers/webs/batman/')
import FlaskApp.config as config

from FlaskApp import app as application
application.secret_key = config.secret_key
application.debug = config.debug
