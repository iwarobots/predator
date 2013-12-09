#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup


class HTML(object):

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
        if self._soup is None:
            self.create_soup()
        return self._soup