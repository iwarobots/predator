#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals


class AbstractCourse(object):
    def __init__(self, course_code):
        self._course_code = course_code

    @property
    def course_code(self):
        return self._course_code


# This seems not to be in use.
class Course(AbstractCourse):
    def __init__(self, course_id, course_code):
        AbstractCourse.__init__(self, course_code)
        self._course_id = course_id

    @property
    def course_id(self):
        return self._course_id


# This seems not to be in use.
class Category(object):
    def __init__(self, name, code):
        self._name = name
        self._code = code

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code


class AbstractLiberalArts(AbstractCourse):
    def __init__(self, course_code, category):
        AbstractCourse.__init__(self, course_code)
        self._category = category

    @property
    def category(self):
        return self._category

    @property
    def course_type(self):
        return '1'


class LiberalArts(AbstractLiberalArts):
    def __init__(self, course_id, course_code, category):
        AbstractLiberalArts.__init__(self, course_code, category)
        self._course_id = course_id

    @property
    def course_id(self):
        return self._course_id


class AbstractElective(AbstractCourse):
    def __init__(self, course_code, dept_id, year):
        AbstractCourse.__init__(self, course_code)
        self._dept_id = dept_id
        self._year = year

    @property
    def dept_id(self):
        return self._dept_id

    @property
    def year(self):
        return self._year

    @property
    def course_type(self):
        return '2'


class Elective(AbstractElective):
    def __init__(self, course_id, course_code, dept_id, year):
        AbstractElective.__init__(self, course_code, dept_id, year)
        self._course_id = course_id

    @property
    def course_id(self):
        return self._course_id
