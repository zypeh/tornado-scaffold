import tornado.web
import tornado.escape

class BaseHandler(tornado.web.RequestHandler):
    ''' Handler the cookie for user sessions '''
    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.write('Error %s' % status_code)
        else:
            self.write('I find your lack of webpages disturbing ...')

    def get_current_user(self):
        user_json = self.get_secure_cookie('user')
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        resp = {'version' : self.settings['api_ver'] }
        self.write(resp)
