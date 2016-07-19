# -*- coding: utf-8 -*-
import binascii, os


def generate_uid(size=32):
    """ Generates a random alphanumeric string of [size] """
    return binascii.hexlify(os.urandom(size/2))


def get_first(obj, default=None):
    return obj[0] if obj else default
