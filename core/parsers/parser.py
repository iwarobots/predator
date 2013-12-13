#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup

from core.parsers.courses import (AbstractLiberalArts, AbstractElective,
                                  LiberalArts, Elective)


# TODO: Refactor this.
def str2(navigable_string, src_encoding=None, dst_encoding=None):
    if src_encoding is None:
        src_encoding = 'utf-8'
    if dst_encoding is None:
        dst_encoding = 'utf-8'
    return navigable_string.encode(src_encoding).decode(dst_encoding)


class HTMLParser(object):

    def __init__(self, html):
        self._html = html

        self._soup = None

    @property
    def html(self):
        return self._html

    @property
    def soup(self):
        return self.get_soup()

    def create_soup(self):
        if self._soup is None:
            self._soup = BeautifulSoup(self.html)

    def get_soup(self):
        self.create_soup()
        return self._soup


class HiddenInputParser(HTMLParser):

    def __init__(self, html):
        HTMLParser.__init__(self, html)

    @property
    def id(self):
        return self.soup.input['id']

    @property
    def value(self):
        return self.soup.input['value']


class BaseParser(HTMLParser):

    def __init__(self, html):
        HTMLParser.__init__(self, html)

    def find_hidden_inputs(self):
        for input_tag in self.soup.find_all('input', {'type': 'hidden'}):
            yield HiddenInputParser(str2(input_tag))

    def parse_hidden_data(self):
        data = {}
        for hidden_input in self.find_hidden_inputs():
            data[hidden_input.id] = hidden_input.value
        return data


class TrParser(HTMLParser):

    def __init__(self, html):
        HTMLParser.__init__(self, html)
        self._tr = self.soup.tr
        self._tds = self._tr.find_all('td')


class AbstractCourseParser(TrParser):

    def __init__(self, html):
        TrParser.__init__(self, html)

    def parse_name(self):
        return str2(self._tds[1].string).rstrip()

    def parse_code(self):
        return str2(self._tds[2].string).rstrip()


class CourseParser(TrParser):

    def __init__(self, html):
        TrParser.__init__(self, html)

    def parse_course_id(self):
        return self._tds[0].span.input['value']

    def is_available(self):
        string = str2(self._tds[11].string).rstrip()
        return string == '人数未满'


class TableParser(BaseParser):

    def __init__(self, html):
        BaseParser.__init__(self, html)

    def select_table(self, table_id):
        return self.soup.find('table', {'id': table_id})


class AbstractLiberalArtsCoursesParser(TableParser):

    def __init__(self, html, category):
        TableParser.__init__(self, html)
        self._category = category

    def parse(self):
        courses = []
        table = self.select_table('gridMain')
        for tr in table.find_all('tr')[1:]:
            p = AbstractCourseParser(str2(tr))
            course = AbstractLiberalArts(p.parse_code(), self._category)
            courses.append(course)
        return courses


class AbstractElectiveCoursesParser(TableParser):

    def __init__(self, html, dept_id, year):
        TableParser.__init__(self, html)
        self._dept_id = dept_id
        self._year = year

    def parse(self):
        courses = []
        table = self.select_table('OutSpeltyEP1_gridMain')
        for tr in table.find_all('tr')[1:]:
            p = AbstractCourseParser(str2(tr))
            course = AbstractElective(p.parse_code(),
                                      self._dept_id,
                                      self._year)
            courses.append(course)
        return courses


class LiberalArtsCoursesParser(TableParser):

    def __init__(self, html, course_code, category):
        TableParser.__init__(self, html)
        self._course_code = course_code
        self._category = category

    def parse(self):
        courses = []
        table = self.select_table('LessonTime1_gridMain')
        for tr in table.find_all('tr')[1:]:
            p = CourseParser(str2(tr))
            course = LiberalArts(p.parse_course_id(),
                                 self._course_code,
                                 self._category)
            courses.append(course)
        return courses


class ElectiveCoursesParser(TableParser):

    def __init__(self, html, course_code, dept_id, year):
        TableParser.__init__(self, html)
        self._course_code = course_code
        self._dept_id = dept_id
        self._year = year

    def parse(self):
        courses = []
        table = self.select_table('LessonTime1_gridMain')
        for tr in table.find_all('tr')[1:]:
            p = CourseParser(str2(tr))
            course = Elective(p.parse_course_id(),
                              self._course_code,
                              self._dept_id,
                              self._year)
            courses.append(course)
        return courses
