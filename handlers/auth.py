from datetime import datetime

import tornado.web
import tornado.auth

from utils import BaseHandler # Check 'user' cookie

## Twitter OAuth support
class TwitterHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        oAuthToken = self.get_secure_cookie('oauth_token')
        oAuthSecret = self.get_secure_cookie('oauth_secret')
        userID = self.get_secure_cookie('user_id')

        if self.get_argumnt('oauth_token', None):
            self.get_authenticated_user(self.async_callback(self._twitter_on_auth))
            return
        elif oAuthToken and oAuthSecret:
            accessToken = {
                'key': oAuthToken,
                'secret': oAuthSecret,
            }
            self.twitter_request('/users/show',
                                 access_token = accessToken,
                                 user_id = userID,
                                 callback = self.async_callback(self._twitter_on_user))
            return

        self.authorize_redirect()

    def _twitter_on_auth(self, user):
        if not user:
            self.clar_all_cookies()
            raise tornado.web.HTTPError(500, 'Twitter authentication failed')

        self.set_secure_cookie('user_id', str(user['id']))
        self.set_secure_cookie('oauth_token', user['access_token']['key'])
        self.set_secure_cookie('oauth_secret', user['access_token']['secret'])

        self.redirect('/')

    def _twitter_on_user(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, "Couldn't retrieve user information")

## Facebook OAuth support
class FacebookLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        userID = self.get_secure_cookie('user_id')

        if self.get_argument('code', None):
            self.get_authenticated_user(
                redirect_uri = '/',
                client_id = self.settings['facebook_api_key'],
                client_secret = self.settings['facebook_secret'],
                code = self.get_argument('code'),
                callback = self._on_facebook_login)
            return
        elif self.get_secure_cookie('access_token'):
            self.redirect('/')
            return

        self.authorize_redirect(
            redirect_uri='/',
            client_id = self.settings['facebook_api_key'],
            extra_params = {'scope': 'publish_stream'},
        )

        def _on_facebook_login(self, user):
            if not user:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500,
                                            'Facebook authentication failed')

            self.set_secure_cookie('user_id', str(user['id']))
            self.set_secure_cookie('user_name', str(user['name']))
            self.set_secure_cookie('access_token', str(user['access_token']))
            self.redirect('/')

## Google OAuth2 support
class GoogleAuthLoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_current_user():
            self.redirect('/products')
            return

        if self.get_argument('code', False):
            user = yield self.get_authenticated_user(redirect_uri=settings.google_redirect_url,
                code=self.get_argument('code'))
            if not user:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500, 'Google authentication failed')

            access_token = str(user['access_token'])
            http_client = self.get_auth_http_client()
            response =  yield http_client.fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token='+access_token)
            if not response:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500, 'Google authentication failed')
            user = json.loads(response.body)
            # save user here, save to cookie or database
            self.set_secure_cookie('trakr', user['email'])
            self.redirect('/products')
            return

        elif self.get_secure_cookie('trakr'):
            self.redirect('/products')
            return

        else:
            yield self.authorize_redirect(
                redirect_uri=settings.google_redirect_url,
                client_id=self.settings['google_oauth']['key'],
                scope=['email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})
