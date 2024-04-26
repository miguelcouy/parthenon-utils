# -*- coding: utf-8 -*-

__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__version__ = '1.0.0'
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@Ooutlook.com'
__status__ = 'Production'

import pytest

import os
import datetime as dt
from cryptography.fernet import Fernet

from source.parthenon_utils import Controller

@pytest.fixture(scope='session')
def base_session():
    return {
        'code_filename': os.path.basename(__file__),
        'code_directory': os.path.dirname(os.path.abspath(__file__)),
        'code_runtime': dt.datetime.now(),
        'code_fernet_key': Fernet.generate_key(),
        'ctrl_create_base_paths': True
    }


def test_controller_basic_init(base_session):
    ctrl = Controller(
        code_filename = base_session['code_filename'],
        code_directory = base_session['code_directory'],
        code_runtime = base_session['code_runtime'],
        code_fernet_key = base_session['code_fernet_key'],
        ctrl_create_base_paths = base_session['ctrl_create_base_paths']
    )

    assert ctrl.code_filename.exists()
    assert ctrl.code_directory == base_session['code_directory']
    assert ctrl.code_runtime == base_session['code_runtime']
    assert ctrl.code_fernet_key == base_session['code_fernet_key']
    assert ctrl.ctrl_create_base_paths == base_session['ctrl_create_base_paths']
