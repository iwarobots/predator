#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup


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


# class TableParser(HTMLParser):
#     def __init__(self, html):
#         HTMLParser.__init__(self, html)
#         self._table_tag = None
#         self._table = []
#
#     def select_table(self, table_id):
#         self._table_tag = self.soup.find('table', {'id': table_id})
#         return self._table_tag
#
#     def parse_table(self):
#         pass

class TableParser(HTMLParser):
    def __init__(self, html):
        HTMLParser.__init__(self, html)

        try:
            self._table_element = self.soup.table
        except:
            raise ValueError('this is not a valid table element')

        self._table = []

    def parse(self):
        if not self._table:
            for tr in self._table_element.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    # filter \n
                    if not str2(td) == '\n':
                        row.append(td)
                self._table.append(row)
        return self._table


class LiberalArtsCoursesParser(TableParser):
    def __init__(self, html):
        TableParser.__init__(self, html)


class ElectiveCoursesParser(BaseParser):
    def __init__(self, html):
        BaseParser.__init__(self, html)
        self._table = None

    def parse(self):
        if not self._table:
            table_element = self.soup.find(
                'table',
                {'id': 'OutSpeltyEP1_gridMain'},
            )
            p = TableParser(str2(table_element))
            self._table = p.parse()
        return self._table

    def a(self):
        names = []
        self.parse()
        for row in self._table[1:]:
            name = str2(row[1].string).rstrip()
            names.append(name)
        return names


class SchedIDNotFound(Exception):
    pass


class SchedPageParser(BaseParser):
    def __init__(self, html):
        BaseParser.__init__(self, html)
        self._table = None
        self._sched_ids = []

    def parse(self):
        if not self._table:
            table_element = self.soup.find(
                'table',
                {'id', 'LessonTime1_gridMain'},
            )
            p = TableParser(str2(table_element))
            self._table = p.parse()
        return self._table

    def is_available(self, sched_id):
        self.parse()
        for row in self._table[1:]:
            val = row[0].span.input['value']
            self._sched_ids.append(val)
            if val == sched_id:
                return str2(row[11].string) == '人数未满'
        return -1
