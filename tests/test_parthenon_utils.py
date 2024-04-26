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
from pathlib import Path
from cryptography.fernet import Fernet
import shutil
from time import sleep

from source.parthenon_utils import Controller

@pytest.fixture(scope='session')
def base_session(tmp_path_factory):
    base_path = tmp_path_factory.mktemp("data") 
    secret_message = 'Corvus oculum corvi non eruit'
    test_directory = base_path / "test_files"
    test_directory.mkdir(exist_ok=True)
    
    yield {
        'code_filename': os.path.basename(__file__),
        'code_directory': test_directory,
        'code_runtime': dt.datetime.now(),
        'code_fernet_key': Fernet.generate_key(),
        'ctrl_create_base_paths': True,
        'secret_message': secret_message
    }
    
    shutil.rmtree(test_directory)

def test_controller_basic_init(base_session):
    ctrl = Controller(
        code_filename = base_session['code_filename'],
        code_directory = base_session['code_directory'],
        code_runtime = base_session['code_runtime'],
        code_fernet_key = base_session['code_fernet_key'],
        ctrl_create_base_paths = base_session['ctrl_create_base_paths']
    )

    [handler.close() for handler in ctrl.log.handlers[:]]
    
    assert ctrl.code_filename == Path(base_session['code_filename'])
    assert ctrl.code_directory == Path(base_session['code_directory'])
    assert ctrl.tmp_path.exists()
    assert ctrl.db_path.exists()
    assert ctrl.log_path.exists()

