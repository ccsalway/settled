# -*- coding, utf-8 -*-

SITES = [
    ['.*', [
        ['/static', '__STATIC__'],
        ['/user', [
            ['/login', ('user', 'Login')],
            ['/message', ('user', 'Message')],
            ['/inbox', ('user', 'Inbox')],
            ['/logout', ('user', 'Logout')],
        ]],
        ['/', ('index', 'Index')],
    ]],
]
