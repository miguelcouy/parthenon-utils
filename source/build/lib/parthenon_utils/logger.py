__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__version__ = '0.0.1'
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@Ooutlook.com'
__status__ = 'Production'

import logging
from logging.handlers import RotatingFileHandler
from sys import stderr
from typing import Union
from pathlib import Path
from datetime import datetime
import re

class Logger:
    def __init__(self, 
                 log_path: Union[str, Path], 
                 code_runtime: Union[str, datetime], 
                 code_filename: Union[str, Path],
                 log_level: int = logging.DEBUG) -> None:
        
        self.log_path = Path(log_path)
        self.code_runtime = str(code_runtime) if isinstance(
            code_runtime, datetime) else code_runtime
        self.code_filename = code_filename
        self.log_level = log_level

        self._ensure_log_directory_exists()

        self.log_filename = self._construct_log_filename()
        self.log_filepath = self.log_path.joinpath(self.log_filename)
        self.log = self._initialize_logger()

    def _sanitize_for_filename(self, name: str) -> str:
        """
        Sanitizes a string to be safe for use as a filename. This method 
        replaces any characters that are not allowed in file names on most 
        operating systems with an underscore.

        Parameters:
        ----------
        name : str
            The string to sanitize.

        Returns:
        -------
        str
            The sanitized string, safe for use as a filename.
        """
        if not isinstance(name, str): name = str(name)
        return re.sub(r'[\\/*?:"<>|]', string = name, repl = '_')
    
    def _construct_log_filename(self) -> str:
        """Generates the log filename from runtime and code filename, ensuring
        the name is safe for use as a filename across different operating 
        systems."""
        
        sanitized_runtime = self._sanitize_for_filename(self.code_runtime)
        sanitized_filename = self._sanitize_for_filename(self.code_filename)
        
        return f"{sanitized_runtime} {sanitized_filename}.log"
    
    def _ensure_log_directory_exists(self):
        """Ensures the log directory exists, creating it if necessary."""
        
        if self.log_path.is_dir() and not self.log_path.exists():
            self.log_path.mkdir(
                parents = True, 
                exist_ok = True
            )

    def _initialize_logger(self) -> logging.Logger:
        """
        Initializes and configures the logger with a custom format and 
        specified logging level.

        This method creates a new logging.Logger instance or retrieves an 
        existing one based on the provided log filename. It sets the logging 
        level to the value specified during the class initialization and
        configures the logger to not propagate messages to higher level loggers. 
        Additionally, it defines a custom log format that includes timestamps,
        logging levels, logger name, module name, function name, thread ID, line
        number, and the log message itself.

        The custom format and datetime format are designed to provide a detailed
        and easily readable log output, facilitating debugging and monitoring of
        application behavior.

        Returns:
        --------
        logging.Logger
            The configured logger instance with the specified level, custom 
            format, and disabled propagation.

        Example Usage:
        --------------
        # Assuming the Logger class has been instantiated with the necessary
        parameters:
        >>> logger_instance = myLogger.log
        # logger_instance is now ready to be used for logging messages 
        # throughout the application, with messages formatted and handled
        # according to the configuration defined in this method.

        Note:
        -----
        The logger's name is set to the filename derived from the code runtime 
        and filename parameters provided during Logger class initialization. 
        This name uniqueness helps in identifying the source of log messages, 
        especially when multiple instances of the Logger class are used within
        the same application.
        """

        logger = logging.getLogger(name = self.log_filename)
        logger.setLevel(self.log_level)
        logger.propagate = False

        log_format = logging.Formatter(
            fmt=' | '.join([
                '%(asctime)s',
                '%(levelname)-8s',
                '%(name)s',
                '%(module)s',
                '%(funcName)s',
                'Thread: %(thread)d',
                'Line: %(lineno)d',
                'Message: %(message)s',
            ]),
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        if not logger.handlers:
            self._setup_log_handlers(logger, log_format)

        return logger

    def _setup_log_handlers(self, 
                            logger: logging.Logger, 
                            log_format: logging.Formatter
                            ) -> None:
        """
        Configures and adds file and stream handlers to the specified logger.

        This method sets up two primary handlers for the logger: a file handler,
        which writes log messages to a file, and a stream handler, which directs
        log messages to stderr. Both handlers are configured to use the 
        specified logging format.

        Parameters:
        ----------
        logger : logging.Logger
            The logger instance to which the file and stream handlers will be 
            added. This logger should already be initialized and have a name
            assigned.

        log_format : logging.Formatter
            The formatting object that defines the format of log messages. This
            format will be applied to both file and stream handlers to ensure 
            consistency in log output.

        Raises:
        ------
        Exception:
            Catches and logs any exception that occurs during the setup of log
            handlers. This is to ensure that any failure in initializing 
            handlers, such as issues with file access permissions or problems 
            creating the file handler, does not cause the application to crash.
            Instead, an error message will be logged using the logger itself,
            indicating the failure to initialize log handlers.

        Notes:
        -----
        - The file handler is configured to append to the log file specified by 
        self.log_filepath, ensuring that logs are preserved across different 
        executions of the code.
        - The stream handler directs log messages to stderr, allowing for 
        real-time monitoring of log messages when running the code in 
        environments that display stderr output.

        Example Usage:
        -------------
        The method is intended to be called within the Logger class during the 
        initialization process and is not designed to be invoked directly by 
        external code. Here is how it is used internally:

            self._setup_log_handlers(logger=self.log, log_format=my_log_format)

        This example assumes that self.log is a pre-initialized logging.Logger 
        instance and my_log_format is a configured logging.Formatter instance.
        """

        try:
            file_handler = logging.FileHandler(
                filename = self.log_filepath, 
                mode = 'a'
            )

            stream_handler = logging.StreamHandler(stream=stderr)

            file_handler.setFormatter(log_format)
            stream_handler.setFormatter(log_format)

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

        except Exception as e:
            logger.error(f'Failed to initialize log handlers: {e}')

    def set_logging_enabled(self, enabled: bool) -> None:
        """
        Enables or disables logging based on the 'enabled' flag. This function
        allows for dynamic control of logging output during runtime, enabling
        logging to be turned off for silent operation or turned on for 
        diagnostic purposes.

        Parameters:
        ----------
        enabled : bool
            If True, logging is enabled at the logger's current level. If False,
            logging is effectively silenced by setting the logger's level to
            a level above CRITICAL.

        Raises:
        ------
        ValueError:
            If the 'enabled' parameter is not a boolean value, a ValueError is
            raised to prevent incorrect usage.

        Notes:
        -----
        - Silencing the logger does not remove handlers but sets their level to
          CRITICAL + 1, which is effectively higher than any standard logging 
          level, thus preventing any logs from being processed.
        - This method affects all handlers attached to the logger, ensuring
          consistent behavior across all output streams.

        Example Usage:
        -------------
        # Assuming an instance of Logger called 'my_logger':
        >>> my_logger.set_logging_enabled(True)  # To enable logging
        >>> my_logger.set_logging_enabled(False) # To silence logging
        """

        if not isinstance(enabled, bool):
            raise ValueError(
                "The 'enabled' parameter must be a boolean value."
            )

        try:
            if enabled:
                for handler in self.log.handlers:
                    handler.setLevel(self.log_level)
            else:
                silence_level = logging.CRITICAL + 1
                for handler in self.log.handlers:
                    handler.setLevel(silence_level)

        except Exception as e:
            self.log.exception(
                "Failed to set logging enabled state to {}: {}".format(
                    enabled, 
                    e
                )
            )

            raise

    def set_log_level(self, level: Union[int, str]) -> None:
        """
        Sets the logging level for the logger and all its handlers. This method
        allows for dynamic adjustment of the verbosity of logging output at 
        runtime.

        Parameters:
        ----------
        level : Union[int, str]
            The logging level to set. This can be specified as an integer (e.g.,
            logging.DEBUG) or as a string (e.g., 'DEBUG') corresponding to the
            standard logging levels.

        Raises:
        ------
        ValueError:
            If the 'level' parameter is not a recognized logging level (either 
            as an integer or a string), a ValueError is raised.

        Notes:
        -----
        - This method adjusts the level of the logger itself as well as all 
          attached handlers, ensuring consistent logging output across all 
          destinations.
        
        Example Usage:
        -------------
        # Assuming an instance of Logger called 'my_logger':
        >>> my_logger.set_log_level(logging.DEBUG)  # Using an integer level
        >>> my_logger.set_log_level('INFO')         # Using a string level
        """

        if isinstance(level, str):
            level = level.upper()
            if hasattr(logging, level):
                level = getattr(logging, level)
            else:
                raise ValueError(
                    f"Invalid logging level string: '{level}'"
                )
            
        elif not isinstance(level, int):
            raise ValueError(
                "Logging level must be an integer or a valid logging level " +
                "string."
            )

        try:
            self.log.setLevel(level)
            for handler in self.log.handlers:
                handler.setLevel(level)

        except Exception as e:
            self.log.exception(
                msg = f"Failed to set logging level to {level}: {e}"
                )
            
            raise RuntimeError(
                f"Failed to set logging level due to an internal error: {e}"
            ) from e
        
    def enable_log_rotation(self, 
                            max_size_bytes: int, 
                            backup_count: int
                            ) -> None:
        """
        Enables log file rotation based on file size. When the current log file
        reaches the specified maximum size, a new file is created, and the old
        file is archived. A specific number of old log files are kept as
        backups.

        Parameters:
        ----------
        max_size_bytes : int
            The maximum size in bytes that the log file can reach before 
            rotation is triggered.

        backup_count : int
            The number of old log files to keep. Files beyond this number are
            deleted.

        Raises:
        ------
        ValueError:
            If `max_size_bytes` or `backup_count` are set to non-positive 
            values.

        Notes:
        -----
        - This function adds a `RotatingFileHandler` to the logger, configured
          with the provided parameters.
        - If the logger already has a `RotatingFileHandler`, it will be replaced
          to reflect the new parameters.

        Example Usage:
        -------------
        # Assuming an instance of Logger called 'my_logger':
        >>> my_logger.enable_log_rotation(
        ...     max_size_bytes=1048576, 
        ...     backup_count=5
        ... )  
        # 1MB file size limit, 5 backups
        """

        if max_size_bytes <= 0:
            raise ValueError("max_size_bytes must be a positive integer.")
        if backup_count <= 0:
            raise ValueError("backup_count must be a positive integer.")

        self.log.handlers = [
            h for h in self.log.handlers 
            if not isinstance(h, RotatingFileHandler)
        ]

        try:
            rotating_handler = RotatingFileHandler(
                filename=self.log_filepath, 
                maxBytes=max_size_bytes, 
                backupCount=backup_count
            )

            formatter = logging.Formatter(
                fmt=' | '.join([
                    '%(asctime)s',
                    '%(levelname)-8s',
                    '%(name)s',
                    '%(module)s',
                    '%(funcName)s',
                    'Thread: %(thread)d',
                    'Line: %(lineno)d',
                    'Message: %(message)s',
                ]),
                datefmt='%Y-%m-%d %H:%M:%S',
            )
            rotating_handler.setFormatter(formatter)

            self.log.addHandler(rotating_handler)

        except Exception as e:
            self.log.exception(
                msg = "Failed to enable log rotation: {}".format(e)
            )

            raise