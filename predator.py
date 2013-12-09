#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import requests

from pages.page import Page


class Component(object):
    
    def __init__(self, session=None):
        # TODO: Problematic initialization
        self._session = session
    
    def sign_in(self, username, password):
        s = requests.session()

        url = 'http://electsys.sjtu.edu.cn/edu/'
        r = s.get(url)
        p = Page(r.text)
        hidden_data = p.parse_hidden_data()

        url = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        data = {
            'txtUserName': username,
            'txtPwd': password,
            'rbtnLst': 1,
            'Button1': '登录',
            }
        data.update(hidden_data)
        r = s.post(url, data=data)

        correct_url = 'http://electsys.sjtu.edu.cn/edu/student/sdtMain.aspx'
        if r.url == correct_url:
            self._username = username
            self._password = password

            self._session = s
    
    def fetch_liberal_arts(self, category):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/speltyCommonCourse.aspx')
        self._session.get(url)
        
        
        


class Sentry(object):

    def __init__(self, session=None):
        self._session = session


class Executor(object):

    def __init__(self):
        self._username = None
        self._password = None

        self._session = None

    def select_liberal_arts(self,
                            course_id,
                            course_code,
                            category,
                            nround):
        url = ('http://electsys.sjtu.edu.cn/edu/'
               'student/elect/electcheck.aspx')
        self._session.get(url, params={'xklc': nround})

        page = self.open_common_course_table(category)

        common_course_categorys = {
            u'人文学科': '420',
            u'社会科学': '430',
            u'自然科学与工程技术': '440',
            u'数学或逻辑学': '450',
            }
        page = self.get_common_course_schedules(category, course_id)

        url = 'http://electsys.sjtu.edu.cn/edu/lesson/viewLessonArrange.aspx'
        params = {
            'kcdm': course_id,
            'xklx': u'通识',
            'redirectForm': 'speltyCommonCourse.aspx',
            'yxdm': '',
            'tskmk': common_course_categorys[category],
            'kcmk': '-1',
            'nj': u'无',
            }
        data = {
            'myradiocategory': bsid,
            'LessonTime1$btnChoose': u'选定此教师',
            }
        page = self.post_from_page(page, url, data, params=params)

        params = {
            'yxdm': '',
            'nj': u'无',
            'kcmk': '-1',
            'txkmk': '',
            'tskmk': common_course_categorys[category],
            }
        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'btnSubmit': u'选课提交',
            }
        return self.post_from_page(page, self.COMMON_COURSE_URL, data, params=params)


p = Executor()
p.sign_in('5114139017', '0112781X')
p.select_liberal_arts(1,1,1,1)
