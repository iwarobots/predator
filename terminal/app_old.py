#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import time
from threading import Thread

import zmq

from core.ctx import ctx
from core.remote_system import RemoteSystem


class UI(Thread):
    def __init__(self, host=None, port='3323'):
        if not host:
            host = '127.0.0.1'
        self.__frontend_socket = ctx.socket(zmq.REQ)
        self.__frontend_socket.connect('tcp://%s:%s' % (host, port))

        self.__user_info = None
        self.__signed_in = False
        self.__targets = []
        self.__targets_accepted = False
        self.__backend_started = False

        Thread.__init__(self)

    def ask_user_info(self):
        username = raw_input('Enter your username: ')
        password = raw_input('Enter your password: ')
        self.__user_info = {
            'username': username,
            'password': password,
        }

    def sign_in(self):
        msg = self.__user_info.copy()
        msg['action'] = 'sign_in'

        self.__frontend_socket.send_json(msg)
        self.__signed_in = self.__frontend_socket.recv_json()

    def show_sign_in_result(self):
        if self.__signed_in:
            print('Sign in succeeded.')
        else:
            print('Sign in failed.')
            #time.sleep(2)
            exit()

    def _ask_course_type(self):
        choice = raw_input('Is it in liberal arts or electives?\n'
                           '[1] Liberal arts\n'
                           '[2] Elective\n')

        # TODO: Better error reporting
        if not choice in ('0', '1', '2'):
            raise ValueError

        return choice

    def _ask_category(self):
        choice = raw_input('Choose category of your target:\n'
                           '[0] 人文\n'
                           '[1] 社科\n'
                           '[2] 自然\n'
                           '[3] 数学\n')

        # TODO: Better error reporting
        if not choice in ('0', '1', '2', '3'):
            raise ValueError
        return choice

    def _ask_course_code(self):
        return raw_input('Enter course code of your target (eg. AV313): ')

    def _ask_course_id(self):
        return raw_input('Enter course id of your target (eg. 354444): ')

    def _ask_dept_id(self):
        return raw_input('Enter department id of your target (eg. 01000): ')

    def _ask_year(self):
        return raw_input('Enter year of your target (eg. 2011): ')

    def _ask_add_more(self):
        choice = raw_input('Do you want to add more targets?[y/n] ')
        add_more = True
        if choice == 'n':
            add_more = False
        return add_more

    def ask_targets(self):
        add_more = True
        while add_more:
            course_type = self._ask_course_type()
            if course_type == '1':
                category = self._ask_category()
                course_code = self._ask_course_code()
                course_id = self._ask_course_id()

                course_info = {
                    'course_id': course_id,
                    'course_code': course_code,
                    'category': category,
                    'course_type': course_type,
                }
                self.__targets.append(course_info)
            elif course_type == '2':
                dept_id = self._ask_dept_id()
                year = self._ask_year()
                course_code = self._ask_course_code()
                course_id = self._ask_course_id()

                course_info = {
                    'course_id': course_id,
                    'course_code': course_code,
                    'dept_id': dept_id,
                    'year': year,
                    'course_type': course_type,
                }
                self.__targets.append(course_info)

            add_more = self._ask_add_more()

    def send_targets(self):
        msg = {
            'action': 'add',
            'targets': self.__targets,
        }
        self.__frontend_socket.send_json(msg)
        self.__targets_accepted = self.__frontend_socket.recv_json()

    def show_targets_sent(self):
        if self.__targets_accepted:
            print('Targets added.')
        else:
            print('Error occurred when adding targets.')

    def start_backend(self):
        raw_input('Press any key to start...')
        msg = {'action': 'start'}
        self.__frontend_socket.send_json(msg)
        self.__backend_started = self.__frontend_socket.recv_json()
        print self.__backend_started

    def show_backend_started(self):
        if self.__backend_started:
            print('Backend started.')
        else:
            print('Backend did not start.')

    def show_status_update(self):
        msg = {'action': 'update'}
        self.__frontend_socket.send_json(msg)
        status = self.__frontend_socket.recv_json()
        print(status)

    def run(self):
        self.ask_user_info()
        self.sign_in()
        self.show_sign_in_result()
        self.ask_targets()
        self.send_targets()
        self.show_targets_sent()
        self.start_backend()
        self.show_backend_started()
        while True:
            self.show_status_update()
            time.sleep(5)


if __name__ == '__main__':
    port = '8978'
    ui = UI(port=port)
    ui.start()

    p = RemoteSystem(port=port)
    p.start()
