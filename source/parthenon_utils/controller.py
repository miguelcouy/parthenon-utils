# -*- coding: utf-8 -*-

__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__version__ = '1.0.0'
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@Ooutlook.com'
__status__ = 'Production'

from pathlib import Path
from typing import Union, Optional
import datetime as dt

from .builder import Builder
from .encrypter import Encrypter, Fernet
from .logger import Logger

class Controller:
    """
    Manages the main operations related to file management, logging, and
    encryption within the system. This class orchestrates the use of Builder for
    file and directory operations, Logger for logging system events, and 
    Encrypter for handling encryption needs based on specified configurations.
    
    Attributes:
        - code_filename : Union[Path, str, None]
            The filename associated with operational context, can be used in 
            logging.
        - code_directory : Union[Path, str, None]
            The base directory for operations and storing files.
        - code_runtime : Union[dt.datetime, str, None]
            A timestamp or descriptive string of the runtime; useful in logging.
        - code_fernet_key : Union[Fernet, str, bytes, None]
            The encryption key used for Encrypter initialization.
        - ctrl_create_base_paths : bool
            Flag to determine if base paths should be automatically created on 
            initialization.
        - builder : Builder
            The Builder object used for file and directory operations.
        - log : Logger.log
            The Logger object's log method used for logging.
        - encrypter : Encrypter
            The Encrypter object used for encryption tasks.
    """

    def __init__(self, 
                 code_filename: Union[Path, str, None] = None,
                 code_directory: Union[Path, str, None] = None, 
                 code_runtime: Union[dt.datetime, str, None] = None,
                 code_fernet_key: Union[Fernet, str, bytes, None] = None,

                 ctrl_create_base_paths: bool = True,
                 ctrl_builder: Optional[Builder] = None,
                 ctrl_log: Optional[Logger] = None,
                 ctrl_encrypter: Optional[Encrypter] = None
                ):
        """
        Initializes the Controller with specific configurations for file paths,
        logging, and encryption. This setup allows for specifying custom
        Builder, Logger, and Encrypter instances or using defaults.

        If custom objects are not provided, the controller initializes default
        objects with given parameters or defaults. Also assigns the log and
        encrypt methods of the Logger and Encrypter to Builder and Encrypter for
        unified logging.
        """


        self.code_filename = Path(code_filename)
        self.code_directory = Path(code_directory)
        self.code_runtime = code_runtime
        self.code_fernet_key = code_fernet_key
        self.ctrl_create_base_paths = ctrl_create_base_paths


        self.builder = ctrl_builder or self.init_builder()
        self.log = ctrl_log or self.init_logger()
        self.encrypter = ctrl_encrypter or self.init_encrypter()
        
        self.builder.ctrl_log = self.log
        self.encrypter.ctrl_log = self.log

    def init_builder(self):
        """
        Initializes the Builder object used within the Controller.
        This method sets up base paths for temporary files, logs, and databases
        if the `ctrl_create_base_paths` is True.
        
        Returns:
            Builder: An initialized Builder object with base paths created if 
            required.
        """


        builder = Builder(
            base_path = self.code_directory
        )

        if self.ctrl_create_base_paths:
            self.tmp_path: Path = builder.ensure_directory(this_path = '.tmp')
            self.log_path: Path = builder.ensure_directory(this_path = '.log')
            self.db_path: Path = builder.ensure_directory(this_path = '.db')

        return builder

    def init_logger(self):
        """
        Initializes the Logger object used within the Controller. This method
        sets up a logging directory and initializes the Logger with this path,
        alongside the runtime and filename context.
        
        The logger's log method is configured to write logs to the '.log'
        directory within the specified `code_directory`. If the '.log' directory
        does not exist, it is created. This setup helps in centralizing log
        management in one location, making it easier to maintain and monitor the
        application's logs.
        
        Returns:
            Logger.log: The logging method from the Logger object, ready to be
            used for logging operations.
        """


        logger = Logger(
            log_path = self.builder.ensure_directory(this_path = '.log'),
            code_runtime = self.code_runtime,
            code_filename = self.code_filename
        ).log

        return logger

    def init_encrypter(self):
        """
        Initializes the Encrypter object used within the Controller. This method
        configures the encryption key for the Encrypter, which is used to handle
        all encryption tasks in the system.
        
        Returns:
            Encrypter: An initialized Encrypter object with the specified 
            encryption key.
        """

    
        encrypter = Encrypter(
            key = self.code_fernet_key
        )

        return encrypter
    


