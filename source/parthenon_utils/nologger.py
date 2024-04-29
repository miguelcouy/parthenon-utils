# -*- coding: utf-8 -*-

__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@outlook.com'
__status__ = 'Production'

class NoLogger:
    def debug(*args, **kwargs): pass
    def info(*args, **kwargs): pass
    def warn(*args, **kwargs): pass
    def error(*args, **kwargs): pass
    def critical(*args, **kwargs): pass