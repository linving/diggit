# -*- coding: utf-8 -*

import re
import tornado.web
import tornado.auth

from utils import encrypt
from utils.auth import WeiboMixin, QQMixin
from model.user import User
from view import BaseHandler


class JoinHandler(BaseHandler):
    error_message = {
        '110': '填写信息不完整。',
        '111': '用户名最多15个字符。',
        '112': 'Email不正确。',
        '113': 'Email已经被使用。',
        '114': '注册失败，请稍后再试试。'
    }

    def get(self):
        self.render('join.html', error=None, name='', email='')

    def post(self):
        name = self.get_argument('name', '')
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')
        if not name or len(name) > 15:
            self.render('join.html', error=111, name=name, email=email)
            return
        match = re.search(r'[\w.-]+@[\w.-]+', email)
        if not match:
            self.render('join.html', error=112, name=name, email=email)
            return
        if not password:
            self.render('join.html', error=110, name=name, email=email)
            return
        user = User.get_by_email(email)
        if user:
            self.render('join.html', error=113, name=name, email=email)
            return
        user = User.new(name, email)
        if user:
            user.update_password(encrypt(password))
        else:
            self.render('join.html', error=114)
        self.set_secure_cookie('user', user.id, expires_days=30)
        self.redirect(self.get_argument('next', '/'))


class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html', error=None, email='')

    def post(self):
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')

        if not (email and password):
            self.render('login.html', error=100, email=email)

        user = User.get_by_email(email)
        if not user:
            self.render('login.html', error=100, email=email)

        if user.get_password() == encrypt(password):
            self.set_secure_cookie('uid', user.id, expires_days=7)
            self.redirect(self.get_argument('next', '/'))
        self.render('login.html', error=100, email=email)


class LogoutHandler(tornado.web.RequestHandler):

    def get(self):
        self.clear_cookie('uid')
        self.redirect('/')


class GoogleLoginHandler(BaseHandler, tornado.auth.GoogleMixin):

    @tornado.web.asynchronous
    def get(self):
        if self.get_argument('openid.mode', None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            self.render('login.html', error=100, email='')
            return

        #parameters = {'email': user['email'], 'open': 'google'}
        #open_user = self.user_dal.get(parameters)

        #user_id = None
        #if not open_user:
        #    open_user = self.user_dal.template()
        #    open_user['name'] = user['name']
        #    open_user['email'] = user['email']
        #    open_user['city'] = user['locale']
        #    open_user['open'] = 'google'
        #    open_user['remote_ip'] = self.request.remote_ip
        #    user_id = self.user_dal.insert(open_user)
        #    if not user_id:
        #        self.render('login.html', error=114, email='')
        #        return
        #else:
        #    user_id = open_user['_id']
        #self.set_secure_cookie('user', str(user_id))
        #self.redirect(self.get_argument('next', '/'))


class WeiboLoginHandler(BaseHandler, WeiboMixin):

    @tornado.web.asynchronous
    def get(self):
        url = (self.request.protocol + '://' + self.request.host +
                  '/open/weibo?next=' +
                  tornado.escape.url_escape(self.get_argument('next', '/')))

        if self.get_argument('oauth_verifier', False):
            self.get_authenticated_user(callback=self._on_auth)
            return
        self.authorize_redirect(callback_uri=url)

    def _on_auth(self, user):
        if not user:
            self.render('login.html', error=100, email='')
            return
        #parameters = {'domain': user['domain'], 'open': 'weibo'}
        #open_user = self.user_dal.get(parameters)

        #user_id = None
        #if not open_user:
        #    open_user = self.user_dal.template()
        #    open_user['name'] = user['name']
        #    open_user['domain'] = user['domain']
        #    open_user['city'] = user['location']
        #    open_user['open'] = 'weibo'
        #    open_user['remote_ip'] = self.request.remote_ip
        #    open_user['photo_url'] = user['profile_image_url']
        #    open_user['middle_photo_url'] = user['avatar_large']
        #    open_user['bio'] = user['description']
        #    open_user['link'] = user['url']
        #    user_id = self.user_dal.insert(open_user)
        #    if not user_id:
        #        self.render('login.html', error=114, email='')
        #        return
        #user_id = open_user['_id']
        #self.set_secure_cookie('user', str(user_id))
        #self.redirect(self.get_argument('next', '/'))


class QQLoginHandler(BaseHandler, QQMixin):
    @tornado.web.asynchronous
    def get(self):
        url = (self.request.protocol + '://' + self.request.host +
                  '/open/qq?next=' +
                  tornado.escape.url_escape(self.get_argument('next', '/')))

        if self.get_argument('oauth_verifier', False):
            self.get_authenticated_user(callback=self._on_auth)
            return
        self.authorize_redirect(callback_uri=url)

    def _on_auth(self, user):
        if not user:
            self.render('login.html', error=100, email='')
            return
        #parameters = {'domain': user['data']['name'], 'open': 'qq'}
        #open_user = self.user_dal.get(parameters)

        #user_id = None
        #if not open_user:
        #    open_user = self.user_dal.template()
        #    user = user['data']
        #    open_user['name'] = user['nick']
        #    open_user['domain'] = user['name']
        #    open_user['city'] = user['location']
        #    open_user['open'] = 'qq'
        #    open_user['remote_ip'] = self.request.remote_ip
        #    open_user['photo_url'] = user['head']
        #    open_user['middle_photo_url'] = user['head']
        #    open_user['link'] = 'http://t.qq.com/%s' % user['name']
        #    user_id = self.user_dal.insert(open_user)
        #    if not user_id:
        #        self.render('login.html', error=114, email='')
        #        return
        #user_id = open_user['_id']
        #self.set_secure_cookie('user', str(user_id))
        #self.redirect(self.get_argument('next', '/'))

