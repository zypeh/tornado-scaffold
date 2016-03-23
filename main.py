import os.path
import time
import signal
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import options

## definitions
from settings import settings
from urls import url_patterns

MAX_WAIT_SECOND_BEFORE_SHUTDOWN = 3

class Unistay_app(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)

def signal_handler(sig, frame):
	logging.warning('[ !! ] Caught signal: {}'.format(sig))
	tornado.ioloop.IOLoop.instance().add_callback(graceful_shutdown)

def graceful_shutdown():
	logging.info('[ ** ] Stopping http server')
	http_server.stop()

	logging.info('[ ** ] Will shutdown in {} seconds'.format(MAX_WAIT_SECOND_BEFORE_SHUTDOWN))
	io_loop = tornado.ioloop.IOLoop.instance()

	deadline = time.time() + MAX_WAIT_SECOND_BEFORE_SHUTDOWN

	def stop_loop():
		now = time.time()
		if now < deadline and (io_loop._callbacks or io_loop._timeouts):
			io_loop.add_timeout(now + 1, stop_loop)
		else:
			io_loop.stop()
			logging.info('[ !! ] Shutdown')
	stop_loop()

def main():
    app = Unistay_app()

    global http_server

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    tornado.ioloop.IOLoop.instance().start()

    logging.info('Exiting now.')

if __name__ == "__main__":
    main()
