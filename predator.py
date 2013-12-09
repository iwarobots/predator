#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import requests

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

        self._username = None
        self._password = None

    def fetch(self, url1, url2, data):
        r = self._session.get(url1)
        p = Page(r.text)
        hidden_data = p.parse_hidden_data()
        data.update(hidden_data)
        return self._session.post(url2, data=data)

    def fetch2(self, current_response, url, data, **kwargs):
        p = Page(current_response.text)
        hidden_data = p.parse_hidden_data()
        data.update(hidden_data)
        return self._session.post(url, data=data, **kwargs)
    
    def fetch_home(self):
        url = 'http://electsys.sjtu.edu.cn/edu/'
        return self._session.get(url)
    
    def sign_in(self, username, password):
        s = requests.session()

        r = self.fetch_home()
        url = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        data = {
            'txtUserName': username,
            'txtPwd': password,
            'rbtnLst': 1,
            'Button1': '登录',
            }
        r = self.fetch2(r, url, data)

        # TODO: Write this into a method.
        correct_url = ('http://electsys.sjtu.edu.cn/'
                       'edu/student/sdtMain.aspx')
        if r.url == correct_url:
            self._username = username
            self._password = password

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
        return self.fetch2(r, url, data)

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
        return self.fetch2(r, url, data)

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
        return self.fetch2(r, url, data)

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
        return self.fetch2(r, url, data)


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
        
        r = self.fetch2(r, url, data, params=params)
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
        return self.fetch2(r, url, data)

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

        r = self.fetch2(r, url, data=data, params=params)
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
        return self.fetch2(r, url, data=data, params=params)
