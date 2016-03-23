import tornado.httpserver
import tornado.web

from utils import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')
