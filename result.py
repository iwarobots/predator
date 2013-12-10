#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals


class Result(object):
    
    def __init__(self, response):
        self._response = response
    
    def __getattr__(self, name):
        if not hasattr(self._response, name):
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (
                    self.__class__.__name__, name))
        return getattr(self._response, name)
