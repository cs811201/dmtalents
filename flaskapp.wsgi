#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp")


from dmworks import app as application
application.secret_key = 'top-secret!'
