#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

from threading import Thread

import zmq
import requests

from common import CONTEXT
from pages.page import Page


class Component(object):

    CATEGORY = {
        '2': '',
        '3': '',
        '4': '',
        '5': '',
    }

    def __init__(self, session=None):
        if session is None:
            self._session = requests.session()
        else:
            self._session = session

        self._username = None
        self._password = None

    def fetch(self, current_response, url, data, **kwargs):
        p = Page(current_response.text)
        hidden_data = p.parse_hidden_data()
        data.update(hidden_data)
        return self._session.post(url, data=data, **kwargs)

    def fetch_home(self):
        url = 'http://electsys.sjtu.edu.cn/edu/'
        return self._session.get(url)

    def sign_in(self, username, password):
        r = self.fetch_home()
        url = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        data = {
            'txtUserName': username,
            'txtPwd': password,
            'rbtnLst': 1,
            'Button1': '登录',
        }
        r = self.fetch(r, url, data)

        # TODO: Write this into a method.
        correct_url = ('http://electsys.sjtu.edu.cn/'
                       'edu/student/sdtMain.aspx')

        result = False
        if r.url == correct_url:
            self._username = username
            self._password = password
            result = True
        return result

    def fetch_liberal_arts_categories(self):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/speltyCommonCourse.aspx')
        return self._session.get(url)

    def fetch_liberal_arts(self, category):
        r = self.fetch_liberal_arts_categories()
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/speltyCommonCourse.aspx')
        data = {
            '__EVENTTARGET': 'gridGModule$ctl0%s$radioButton' % category,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'gridGModule$ctl0%s$radioButton' % category: 'radioButton',
        }
        return self.fetch(r, url, data)

    def fetch_liberal_arts_course(self, course_code, category):
        r = self.fetch_liberal_arts(category)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/speltyCommonCourse.aspx')
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'gridGModule$ctl0%s$radioButton' % category: 'radioButton',
            'myradiogroup': course_code,
            'lessonArrange': '课程安排',
        }
        return self.fetch(r, url, data)

    def fetch_depts(self):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/outSpeltyEP.aspx')
        return self._session.get(url)

    def fetch_dept(self, dept, grade):
        r = self.fetch_depts()
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/outSpeltyEP.aspx')
        data = {
            'OutSpeltyEP1$dpYx': dept,
            'OutSpeltyEP1$dpNj': grade,
            'OutSpeltyEP1$btnQuery': '查 询',
        }
        return self.fetch(r, url, data)

    def fetch_dept_course(self, course_code, dept, grade):
        r = self.fetch_dept(dept, grade)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/outSpeltyEP.aspx')
        data = {
            'OutSpeltyEP1$dpYx': dept,
            'OutSpeltyEP1$dpNj': grade,
            'myradiogroup': course_code,
            'OutSpeltyEP1$lessonArrange': '课程安排',
        }
        return self.fetch(r, url, data)


class Sentry(Component):
    def __init__(self, session=None):
        Component.__init__(self, session)


class Executor(Component):
    def __init__(self, session=None):
        Component.__init__(self, session)

    def select_liberal_arts(self,
                            course_id,
                            course_code,
                            category,
                            nround):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/electcheck.aspx')
        self._session.get(url, params={'xklc': nround})

        r = self.fetch_liberal_arts_course(course_code, category)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'lesson/viewLessonArrange.aspx')
        data = {
            'myradiogroup': course_id,
            'LessonTime1$btnChoose': '选定此教师',
        }
        params = {
            'kcdm': course_code,
            'xklx': '通识',
            'redirectForm': 'speltyCommonCourse.aspx',
            'yxdm': '',
            'tskmk': '4%s0' % category,
            'kcmk': '-1',
            'nj': '无',
        }

        r = self.fetch(r, url, data, params=params)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/speltyCommonCourse.aspx')
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'btnSubmit': '选课提交',
        }
        params = {
            'yxdm': '',
            'nj': '无',
            'kcmk': '-1',
            'txkmk': '',
            'tskmk': '4%s0' % category,
        }
        return self.fetch(r, url, data=data, params=params)

    def select_elective(self, course_id, course_code, dept, grade, nround):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/electcheck.aspx')
        self._session.get(url, params={'xklc': nround})

        r = self.fetch_dept_course(course_code, dept, grade)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'lesson/viewLessonArrange.aspx')
        data = {
            'myradiogroup': course_id,
            'LessonTime1$btnChoose': '选定此教师',
        }
        params = {
            'kcdm': course_code,
            'xklx': '选修',
            'redirectForm': 'outSpeltyEP.aspx',
            'yxdm': dept,
            'nj': grade,
            'kcmk': '-1',
            'txkmk': '-1',
        }

        r = self.fetch(r, url, data=data, params=params)
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/outSpeltyEP.aspx')
        data = {
            'OutSpeltyEP1$dpYx': dept,
            'OutSpeltyEP1$dpNj': grade,
            'OutSpeltyEP1$btnSubmit': '选课提交',
        }
        params = {
            'yxdm': dept,
            'nj': grade,
            'kcmk': '-1',
            'txkmk': '-1',
            'tskmk': '',
        }
        return self.fetch(r, url, data=data, params=params)


class Predator(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.__socket = CONTEXT.socket(zmq.REP)
        self.__socket.bind('tcp://127.0.0.1:3323')

        self.__session = requests.session()
        self.__sentry = Sentry(self.__session)
        self.__executor = Executor(self.__session)

        self.__targets = []

    def get_command(self, msg):
        return msg['command']

    def receive(self, msg):
        if self.get_command(msg) == 'sign_in':
            res = self.__executor.sign_in(msg['username'], msg['password'])
            self.__socket.send_json(res)

    def run(self):
        while True:
            msg = self.__socket.recv_json()
            self.receive(msg)