# -*- coding, utf-8 -*-

SITES = [
    ['(localhost|127.0.0.1|52.19.237.227)', [
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
