#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('templates\index.html')


class SignInHandler(tornado.web.RequestHandler):

    def post(self):
        a = self.get_argument('username')
        b = self.get_argument('password')
        self.write(a)
        self.write(b)
        self.write('1')


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/signin', SignInHandler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()