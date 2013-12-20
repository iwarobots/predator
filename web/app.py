#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import tornado.ioloop
import tornado.web

from core.remote_system import RemoteSystem

predator = RemoteSystem()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        res = predator.sign_in(username, password)
        if res:
            self.write('ok')
        else:
            self.write('failed')
            self.redirect('/')


class AddCourseHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('add_course.html')


if __name__ == "__main__":
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/login', LoginHandler),
        (r'/addcourse', AddCourseHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()