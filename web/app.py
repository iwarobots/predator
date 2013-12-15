#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import time

import tornado.ioloop
import tornado.web

from core.predator import Predator

predator = Predator()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class SignInHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        res = predator.sign_in(username, password)
        if res:
            self.write('ok')
        else:
            self.write('failed')
            self.redirect('/')


class SelectCourseHandler(tornado.web.RequestHandler):
    def get(self):
        pass


if __name__ == "__main__":
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/signin', SignInHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()