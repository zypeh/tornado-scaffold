import os
import environment
import logging

import tornado
import tornado.template
from tornado.options import define, options

import motor

from handlers.error import ErrorHandler

# Simple hacks
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

define("port", default = 8080, help = "port", type = int)
define("config", default = None, help = "config")
define("debug", default = False, help = "debug")
tornado.options.parse_command_line()

## PATHS
STATIC_ROOT = path(ROOT, 'static')
TEMPLATE_ROOT = path(ROOT, 'templates')


settings = {}
settings['default_handler_class'] = ErrorHandler,
settings['default_handler_args'] = dict(status_code = 404)

settings['static_path'] = STATIC_ROOT
settings['template_path'] = TEMPLATE_ROOT
settings['xsrf_cookies'] = False
settings['db'] = motor.MotorClient().tornado
settings['cookie_secret'] = "RANDOMSTUFF"
settings['login_url'] = '/signin'
settings['gzip'] = True
settings['debug'] = True

settings['smtp_host'] = 'smtp.gmail.com'
settings['smtp_port'] = '465' # 587 for non-SSL, 465 for SSL
settings['smtp_username'] = 'EMAIL'
settings['smtp_password'] = 'EMAILPASSWORD' # password

settings['twitter_consumer_key'] = 'CONSUMERKEY'
settings['twitter_consumer_secret'] = 'CONSUMERSECRET'

settings['facebook_api_key'] = 'FACEBOOKAPIKEY'
settings['facebook_secret'] = 'FACEBOOKSECRET'
