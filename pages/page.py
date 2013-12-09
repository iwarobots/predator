#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup

from pages.html import HTML


def ns2str(ns, src_encoding=None, dst_encoding=None):
    if src_encoding is None:
        src_encoding = 'utf-8'
    if dst_encoding is None:
        dst_encoding = 'utf-8'

    return ns.encode(src_encoding).decode(dst_encoding)


class HiddenInput(HTML):

    def __init__(self, html):
        HTML.__init__(self, html)

    # TODO: Needs better name
    @property
    def _ref(self):
        return self.soup.input

    @property
    def id(self):
        return self._ref['id']

    @property
    def value(self):
        return self._ref['value']


class Page(HTML):

    def __init__(self, html):
        HTML.__init__(self, html)

    def find_hidden_inputs(self):
        for input_tag in self.soup.find_all('input', {'type': 'hidden'}):
            yield HiddenInput(ns2str(input_tag))

    def parse_hidden_data(self):
        data = {}

        for hidden_input in self.find_hidden_inputs():
            data[hidden_input.id] = hidden_input.value

        return data
