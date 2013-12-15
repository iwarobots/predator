#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO: # 001 Don't know how to deal with the situation
#       that a user signs into the system form other accesses,
#       i.e. Google Chrome, after our service has started.

# TODO: # 002 Handle successful selection and the user is signed
#       out by the server. I don't know what strategy the server
#       uses in the second and third round. But this is the
#       we encounter in the first round.


from __future__ import absolute_import, unicode_literals
from threading import Thread
import Queue
import time

import requests

from core.parsers import BaseParser, SchedTableParser


class Predator(object):
    _HOME = 'http://electsys.sjtu.edu.cn/edu/'
    _REQUIRED = ('http://electsys.sjtu.edu.cn/edu/'
                 'student/elect/speltyRequiredCourse.aspx')
    _LIBERAL_ARTS = ('http://electsys.sjtu.edu.cn/edu/'
                     'student/elect/speltyCommonCourse.aspx')
    _ELECTIVE = ('http://electsys.sjtu.edu.cn/edu/'
                 'student/elect/outSpeltyEP.aspx')
    _SCHEDULES = ('http://electsys.sjtu.edu.cn/edu/'
                  'lesson/viewLessonArrange.aspx')

    def __init__(self, session=None, nround='1'):
        if session is None:
            self._session = requests.session()
        else:
            self._session = session

        self._round = nround
        self._round_selected = False

        self._username = None
        self._password = None

    def post_from_current_response(
            self, current_response, url, data=None, **kwargs):

        p = BaseParser(current_response.text)
        hidden_data = p.parse_hidden_data()
        data.update(hidden_data)
        return self._session.post(url, data=data, **kwargs)

    def download_home(self):
        # Tested
        return self._session.get(self._HOME)

    def sign_in(self, username, password):
        # Tested
        r = self.download_home()
        url = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        data = {
            'txtUserName': username,
            'txtPwd': password,
            'rbtnLst': 1,
            'Button1': '登录',
        }
        r = self.post_from_current_response(r, url, data)

        # TODO: Write this into a method.
        correct_url = ('http://electsys.sjtu.edu.cn/'
                       'edu/student/sdtMain.aspx')

        result = False
        if r.url == correct_url:
            self._username = username
            self._password = password
            result = True
        return result

    def select_round(self):
        # Tested
        if not self._round_selected:
            url = ('http://electsys.sjtu.edu.cn/edu/'
                   'student/elect/electcheck.aspx')
            self._session.get(url, params={'xklc': self._round})

    def download_liberal_arts_categories(self):
        # Tested
        return self._session.get(self._LIBERAL_ARTS)

    def _download_liberal_arts_from_categories(
            self, response, category):

        # Tested
        data = {
            '__EVENTTARGET': 'gridGModule$ctl0%s$radioButton' % category,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'gridGModule$ctl0%s$radioButton' % category: 'radioButton',
        }
        return self.post_from_current_response(
            response, self._LIBERAL_ARTS, data
        )

    def download_liberal_arts(self, category):
        # Tested
        r = self.download_liberal_arts_categories()
        return self._download_liberal_arts_from_categories(
            r, category
        )

    def _download_liberal_arts_schedule_from_courses(
            self, response, course_code, category):

        # Tested
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'gridGModule$ctl0%s$radioButton' % category: 'radioButton',
            'myradiogroup': course_code,
            'lessonArrange': '课程安排',
        }
        return self.post_from_current_response(
            response, self._LIBERAL_ARTS, data
        )

    def download_liberal_arts_schedule(self, course_code, category):
        # Tested
        r = self.download_liberal_arts(category)
        return self._download_liberal_arts_schedule_from_courses(
            r, course_code, category
        )

    def download_elective(self, dept_id, year):
        # Tested
        r = self._session.get(self._ELECTIVE)
        data = {
            'OutSpeltyEP1$dpYx': dept_id,
            'OutSpeltyEP1$dpNj': year,
            'OutSpeltyEP1$btnQuery': '查 询',
        }
        return self.post_from_current_response(r, self._ELECTIVE, data)

    def _download_elective_schedule_from_courses(
            self, response, course_code, dept_id, year):

        # Tested
        data = {
            'OutSpeltyEP1$dpYx': dept_id,
            'OutSpeltyEP1$dpNj': year,
            'myradiogroup': course_code,
            'OutSpeltyEP1$lessonArrange': '课程安排',
        }
        return self.post_from_current_response(
            response, self._ELECTIVE, data
        )

    def download_elective_schedule(self, course_code, dept_id, year):
        # Tested
        r = self.download_elective(dept_id, year)
        return self._download_elective_schedule_from_courses(
            r, course_code, dept_id, year
        )

    def submit_selections(self):
        r = self._session.get(self._REQUIRED)
        data = {
            'SpeltyRequiredCourse1$Button1': '选课提交',
        }
        return self.post_from_current_response(
            r, self._REQUIRED, data=data
        )

    def is_submitted(self, response):
        # TODO: Update this block when 2nd and 3rd round comes.
        result = False
        if self._round == '1':
            kw = '已提交，请等待教务处的微调结果！'
            if kw in response.text:
                result = True
        if self._round == '2':
            result = True
        if self._round == '3':
            result = True
        return result

    def is_available(self, resp, sched_id):
        p = SchedTableParser(resp.text)
        return p.is_available(sched_id)

    def _select_schedule(self, sched_id, func, args=(), params=None):
        self.select_round()
        resp = func(*args)
        available = self.is_available(resp, sched_id)
        selected = False
        if available:
            data = {
                'myradiogroup': sched_id,
                'LessonTime1$btnChoose': '选定此教师',
            }
            resp = self.post_from_current_response(
                resp, self._SCHEDULES, data, params=params
            )
            if resp.status_code == 200:
                selected = True
        return selected

    def _select_course(self, func, args=()):
        is_submitted = False
        selected = func(*args)
        if selected:
            resp = self.submit_selections()
            is_submitted = self.is_submitted(resp)
        return is_submitted

    def select_liberal_arts_schedule(self, sched_id, course_code, category):
        # TODO: If the number of courses reaches the limit, an error
        #       page will be presented here.
        return self._select_schedule(
            sched_id,
            self.download_liberal_arts_schedule,
            args=(course_code, category),
            params={
                'kcdm': course_code,
                'xklx': '通识',
                'redirectForm': 'speltyCommonCourse.aspx',
                'yxdm': '',
                'tskmk': '4%s0' % category,
                'kcmk': '-1',
                'nj': '无',
            }
        )

    def select_liberal_arts(self, sched_id, course_code, category):
        return self._select_course(
            self.select_liberal_arts_schedule,
            args=(sched_id, course_code, category),
        )

    def select_elective_schedule(self, sched_id, course_code, dept_id, year):
        # TODO: If the number of courses reaches the limit, an error
        #       page will be presented here.
        return self._select_schedule(
            sched_id,
            self.download_elective_schedule,
            args=(course_code, dept_id, year),
            params={
                'kcdm': course_code,
                'xklx': '选修',
                'redirectForm': 'outSpeltyEP.aspx',
                'yxdm': dept_id,
                'nj': year,
                'kcmk': '-1',
                'txkmk': '-1',
            }
        )

    def select_elective(self, sched_id, course_code, dept_id, year):
        return self._select_course(
            self.select_elective_schedule,
            args=(sched_id, course_code, dept_id, year),
        )


class Predator2(object):
    def __init__(self, nround=1, port='3323'):
        self.__backend_socket = ctx.socket(zmq.REP)
        self.__backend_socket.bind('tcp://127.0.0.1:%s' % port)

        self.__session = requests.session()
        self.__sentry = Sentry(self.__session, nround)
        self.__executor = Executor(self.__session, nround)
        self.__status_updates = Queue.Queue()

        self.__targets = []
        self.__captured = []
        self.__started = False

    def loop(self):
        while True:
            # Ask sentry to check if courses is available.
            for t in self.__targets:
                available = self.__sentry.is_available(t)
                if available:
                    msg = 'Course %s is available.' % t.sched_id
                    self.__status_updates.put_nowait(msg)

                    # Should update the targets list.
                    # Should update status.
                    # Should sign in again.
                    result = self.__executor.select(t)
                    if result:
                        pass
                    else:
                        pass

                else:
                    time.sleep(1)

            time.sleep(5)

    def handle_sign_in(self, msg):
        #{
        #    'action': 'sign_in'
        #    'username': '',
        #    'password': '',
        #}
        res = self.__executor.sign_in(msg['username'], msg['password'])
        self.__backend_socket.send_json(res)

    def handle_add(self, msg):
        #{
        #    '0': None,    # Required
        #    '1': LiberalArts,
        #    '2': Elective,
        #}
        try:
            targets = msg['targets']
            for t in targets:
                if t['course_type'] == '0':
                    # Not implemented
                    pass
                elif t['course_type'] == '1':
                    course = LiberalArts(t['sched_id'],
                                         t['course_code'],
                                         t['category'])
                elif t['course_type'] == '2':
                    course = Elective(t['sched_id'],
                                      t['course_code'],
                                      t['dept_id'],
                                      t['year'])

                # TODO: In the future, we can verify if provided course
                #       information is valid.
                self.__targets.append(course)

            self.__backend_socket.send_json(True)
        except:
            self.__backend_socket.send_json(False)

    def handle_update(self, msg):
        updates = []
        while not self.__status_updates.empty():
            update = self.__status_updates.get_nowait()
            updates.append(update)
        self.__backend_socket.send_json(updates)

    def handle_start(self, msg):
        if not self.__started:
            self.__backend_socket.send_json(True)
            t = Thread(target=self.loop)
            t.start()

    def receive(self, msg):
        handlers = {
            'sign_in': self.handle_sign_in,
            'add': self.handle_add,
            'start': self.handle_start,
            'update': self.handle_update,
        }
        action = msg['action']
        if action in handlers:
            handlers[action](msg)
        else:
            # Needs better handler
            pass

    def start(self):
        while True:
            msg = self.__backend_socket.recv_json()
            self.receive(msg)
#
#
# p = Predator()
# p.sign_in('5114139017', '0112781X')
# #print p.select_liberal_arts('354432', 'CA903', '4')
# print p.select_elective('354622', 'AM016', '33000', '2011')