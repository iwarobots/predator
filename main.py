#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import time
import json

import zmq

from common import CONTEXT
from predator import Predator


def main():
    p = Predator()
    p.start()
    socket = CONTEXT.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:3323')

    username = raw_input('Enter your username: ')
    password = raw_input('Enter your password: ')
    user_info = {
        'username': username,
        'password': password,
    }

    msg = user_info.copy()
    msg['command'] = 'sign_in'

    socket.send_json(msg)
    res = socket.recv_json()
    if res:
        choice = raw_input('Successfully signed in. Save your account?[y/n]')
        if choice == 'y':
            json.dump(user_info, open('user_info.json', 'w'))
    else:
        print('Sign in failed.')
        time.sleep(2)
        exit()

    choice = raw_input('Is it in liberal arts or electives?\n'
                       '[1] Liberal arts'
                       '[2] Elective')
    if choice == '1':
        pass
    elif choice == '2':
        pass
    prompt = ('Choose the category of your target:\n'
              '[1] 人文\n'
              '[2] 社科\n'
              '[3] 自然\n'
              '[4] 数学\n')
    raw_input(prompt)


if __name__ == '__main__':
    main()