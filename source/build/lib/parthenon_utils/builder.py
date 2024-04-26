# -*- coding: utf-8 -*-

__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__version__ = '0.0.1'
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@outlook.com'
__status__ = 'Production'

from pathlib import Path
from typing import Callable, Union, Optional, List, Dict
from datetime import datetime
from functools import wraps
import os
import shutil
import re

from .nologger import NoLogger


def ensure_path(func: Callable) -> Callable:
    """
    Decorator to ensure that any keyword argument ending with '_path' passed to
    the decorated function is an instance of pathlib.Path. If a string is 
    provided, it is converted into a pathlib.Path object. This conversion allows
    the decorated function to operate with path arguments more flexibly.

    Parameters
    ----------
    func : Callable
        The function to be decorated.

    Returns
    -------
    Callable
        The decorated function with path arguments automatically converted to 
        Path objects.
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_kwargs = {
            k: (
                Path(v) 
                if k.endswith('_path') and isinstance(v, str) 
                else v
            ) 
            for k, v 
            in kwargs.items()
        }
        return func(*args, **new_kwargs)

    return wrapper

class Builder:
    """
    A utility class that provides various methods to handle file and directory
    operations. It supports creating directories, deleting files or directories,
    renaming files, and searching for files based on different criteria such as
    name, size, or extension. It can also perform more complex tasks like
    comparing directories or copying/moving entire directories.
    
    Attributes:
        - base_path (Optional[Path]): 
            The base path for all file operations. If specified, all relative
            paths in methods will be appended to this base path. This is helpful
            to centralize file operations within a specific directory.
        - ctrl_log (Logger):
            The logging object used to log messages about file operations. By 
            default, it uses a 'NoLogger' which does not perform any logging
            unless replaced with a functional Logger.
    """


    def __init__(self, 
                 base_path: Optional[Path] = None,
                 ) -> None:
        
        self.base_path = Path(
            base_path
        ) if isinstance(
            base_path, str
        ) else base_path
        
        self.ctrl_log = NoLogger()


    @ensure_path
    def ensure_directory(self, this_path: Path) -> Path:
        """
        Ensure that a directory exists at the specified path.
        If the directory does not exist, it is created. The path can be either
        a string or a pathlib.Path object.

        Parameters
        ----------
        this_path : Union[str, Path]
            The path to the directory to ensure.

        Returns
        -------
        Path
            The pathlib.Path object representing the ensured directory path.
        """
        
        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)

        os.makedirs(
            name = this_path,
            exist_ok = True
        )

        self.ctrl_log.debug(
            "Directory ensured at path: %s",
            this_path
        )

        return this_path


    @ensure_path
    def bulldoze(self, this_path: Path) -> None:
        """
        Removes a file or directory at the specified path. If the path points to
        a file, the file is removed. If the path points to a directory, the 
        directory and all its contents are removed recursively.

        Parameters
        ----------
        this_path : Union[str, Path]
            The path to the file or directory to remove.

        Returns
        -------
        None
        """
        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)

        self.ctrl_log.debug(
            "Attempting to remove: %s",
            this_path
        )


        if this_path.is_file():
            os.remove(this_path)

            self.ctrl_log.debug(
                "File successfully removed: %s",
                this_path
            )

        elif this_path.is_dir():
            shutil.rmtree(this_path)

            self.ctrl_log.debug(
                "Directory and contents successfully removed: %s",
                this_path
            )



    def time_to_dt(time: float, format: str = '%Y-%m-%d %H:%M:%S') -> str:
        """ Converts a timestamp to a formatted datetime string. """
        return datetime.fromtimestamp(time).strftime(format)


    @ensure_path
    def _search_files(self,
                      this_path: Path,
                      filter_func: Callable[[Path], bool],
                      deep_search: bool = True
                      ) -> List[Path]:
        """
        Search for files within a directory hierarchy, optionally applying a
        filter.

        Parameters
        ----------
        this_path : Path
            The root directory to start the search from.
        filter_func : Callable[[Path], bool]
            A function to filter the files. Should return True if the file
            matches.
        deep_search : bool
            If True, perform a recursive search including all subdirectories.
            If False, search only the immediate directory (Not used in this 
            version).

        Returns
        -------
        List[Path]
            A list of Path objects representing the files found.
        """
        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)

        found_files = []

        if deep_search:
            for file_path in this_path.rglob('*'):
                if filter_func(file_path):
                    found_files.append(file_path)

                    self.ctrl_log.debug(
                        "File found: %s",
                        file_path
                    )
                    
        else:
            for file_path in this_path.glob('*'):
                if filter_func(file_path) and file_path.is_file():
                    found_files.append(file_path)

                    self.ctrl_log.debug(
                        "File found: %s",
                        file_path
                    )
        
        self.ctrl_log.debug(
            "Total files found: %s",
            len(found_files)
        )
            
        return found_files


    @ensure_path
    def find_files_by_name(self,
                           this_path: Path,
                           hint: str,
                           deep_search: bool = True,
                           is_hint_regex: bool = False
                           ) -> List[Path]:
        """
        method to find files within a directory hierarchy by name.

        This method recursively searches for files within the directory tree
        rooted at 'this_path' and returns a list of paths to files whose names
        match the provided hint. The search can be made case-insensitive and can
        use regular expressions for the hint.

        Parameters
        ----------
        this_path : Union[str, Path]
            The root directory to start the search.

        hint : str
            The hint to match file names against. If 'is_hint_regex' is False,
            the hint is treated as a substring to search for within file names.
            If 'is_hint_regex' is True, the hint is treated as a regular
            expression.

        deep_search : bool, optional
            If True, the search will be recursive, including all subdirectories.
            If False, only the immediate children of 'this_path' will be
            searched.

        is_hint_regex : bool, optional
            If True, the hint is treated as a regular expression pattern.
            If False, the hint is treated as a substring to search for within
            file names.

        Returns
        -------
        List[Path]
            A list of pathlib.Path objects representing the paths to the found
            files.
        """

        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)
        
        self.ctrl_log.debug(
            ' '.join(
                "Starting search for files at %s by name using hint %s",
                "with deep search set to %s and regex set to %s"
            ),
            this_path, hint, deep_search, is_hint_regex
        )

        if is_hint_regex:
            pattern = re.compile(hint, re.IGNORECASE)
            filter_func = lambda p: bool(pattern.search(p.name))

        else:
            filter_func = lambda p: hint.lower() in p.name.lower()

        return Builder._search_files(this_path, filter_func, deep_search)


    @ensure_path
    def find_files_by_extension(self,
                                this_path: Path,
                                extensions: Union[str, List[str]],
                                deep_search: bool = True,
                                is_ext_regex: bool = False
                                ) -> List[Path]:
        """
        method to find files within a directory hierarchy by extension.

        This method recursively searches for files within the directory tree
        rooted at 'this_path' and returns a list of paths to files whose
        extensions match the provided extensions. The search can be made
        case-insensitive and can use regular expressions for the extensions.

        Parameters
        ----------
        this_path : Union[str, Path]
            The root directory to start the search.

        extensions : Union[str, List[str]]
            The extensions to match file extensions against. If 'is_ext_regex'
            is False, each extension should be a string representing the
            extension (e.g., 'txt', '.pdf'). If 'is_ext_regex' is True, each
            extension should be a regular expression pattern.

        deep_search : bool, optional
            If True, the search will be recursive, including all subdirectories.
            If False, only the immediate children of 'this_path' will be
            searched.

        is_ext_regex : bool, optional
            If True, the extensions are treated as regular expression patterns.
            If False, the extensions are treated as literal extensions.

        Returns
        -------
        List[Path]
            A list of pathlib.Path objects representing the paths to the found
            files.
        """

        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)

        if not isinstance(extensions, list):
            extensions = [extensions]

        self.ctrl_log.debug(
            ' '.join(
                "Starting search for files at %s by name using hint %s",
                "with deep search set to %s and regex set to %s"
            ),
            this_path, extensions, deep_search, is_ext_regex
        )

        if is_ext_regex:
            patterns = [
                re.compile(ext, re.IGNORECASE)
                for ext in extensions
            ]

            filter_func = lambda p: any(
                pattern.search(p.suffix) for pattern in patterns
            )

        else:
            if not all(ext.startswith('.') for ext in extensions):
                extensions = [
                    '.' + ext
                    if not ext.startswith('.')
                    else ext
                    for ext in extensions
                ]

            filter_func = lambda p: p.suffix in extensions

        return Builder._search_files(this_path, filter_func, deep_search)

    @ensure_path
    def find_files_by_size(self,
                           this_path: Path,
                           min_size: int = None,
                           max_size: int = None,
                           deep_search: bool = True
                           ) -> List[Path]:
        """
        method to find files within a directory hierarchy based on file
        size criteria.

        This method recursively searches for files within the directory tree 
        rooted at 'this_path' and returns a list of paths to files that meet the
        size criteria specified by min_size and max_size parameters.

        Parameters
        ----------
        this_path : Union[str, Path]
            The root directory to start the search from.
        min_size : int, optional
            The minimum file size in bytes. Files smaller than this will be 
            excluded from the results. If None, no minimum size filter is 
            applied. Default is None.
        max_size : int, optional
            The maximum file size in bytes. Files larger than this will be 
            excluded from the results. If None, no maximum size filter is 
            applied. Default is None.
        deep_search : bool, optional
            If True, perform a recursive search including all subdirectories.
            If False, search only the immediate directory. Default is True.

        Returns
        -------
        List[Path]
            A list of pathlib.Path objects representing the paths to the found
            files that meet the size criteria.
        """
        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)

        self.ctrl_log.debug(
            ' '.join(
                "Starting search for files by size at %s.",
                "Min size: %s bytes.",
                "Max size: %s bytes.",
                "Deep search: %s"
            ),
            this_path, min_size, max_size, deep_search
        )

        def size_filter(file_path: Path) -> bool:
            size = file_path.stat().st_size
            if min_size is not None and size < min_size: return False
            if max_size is not None and size > max_size: return False
            return True

        return Builder._search_files(this_path, size_filter, deep_search)
    
    @ensure_path
    def rename_files(self,
                     this_path: Path,
                     prefix: Optional[str] = None,
                     name: Optional[str] = None,
                     suffix: Optional[str] = None
                     ) -> List[Path]:
        """
        Renames files within a specified directory or directories, allowing for
        the addition of prefixes, custom file names, and suffixes. This static
        method can handle a single Path object or list of Path objects pointing
        to the directories containing files to be renamed. If a directory is
        provided, it will rename all files within it based on the given
        parameters.

        Parameters
        ----------
        this_path : Path
            A single Path object or a list of Path objects representing the
            directory or directories containing files to be renamed. If a list
            is provided, each Path in the list should point to valid directory.

        prefix : Optional[str], optional
            A string to be added as a prefix to each file's name. If None, no
            prefix is added. Default is None.

        name : Optional[str], optional
            A new name to replace the original file name (excluding the
            extension). If None, the original file name (stem) is retained.
            This allows for complete renaming of the file while preserving its
            extension. Default is None.

        suffix : Optional[str], optional
            A string to be added as a suffix to each file's name, appearing
            before the file's extension. If None, no suffix is added. Default is
            None.

        Returns
        -------
        List[Path]
            A list of Path objects representing the renamed files. Each Path in
            the list points to the new location and name of the renamed file.

        Notes
        -----
        - The `@ensure_path` decorator ensures that `this_path` is converted to
        a Path object if it is not already one, facilitating consistent handling
        of file paths.

        - The `@exception_handler` decorator wraps the method to handle common
        file system errors gracefully, such as permission errors or files not
        found, providing a more user-friendly error message.

        - This method can be particularly useful for batch processing of files,
        such as renaming a large number of files to conform to a specific naming
        convention or structure.
        """
        if isinstance(this_path, Path):
            this_path = [this_path]

        if isinstance(self.base_path, Path):
            this_path = [self.base_path.joinpath(path) for path in this_path]

        renamed_files = []
        for file in this_path.iterdir():
            if file.is_file():
                name_without_ext = file.stem

                new_name = "{}{}{}{}".format(
                    prefix if prefix else '',
                    name if name else name_without_ext,
                    suffix if suffix else '',
                    file.suffix
                )

                new_file_path = file.rename(this_path / new_name)

                self.ctrl_log.debug(
                    "Renaming file %s to %s",
                    file, new_file_path
                )
                    
                renamed_files.append(new_file_path)

        self.ctrl_log.debug(
            "Total files renamed: %s",
            len(renamed_files)    
        )

        return renamed_files


    @ensure_path
    def file_information(self,
                         this_path: Union[Path, List[Path]]
                         ) -> Dict[str, dict]:
        """
        Retrieves detailed information for a given file or a list of files.
        For each valid file, it returns a dictionary containing the file's name,
        path, size, creation and modification times, and octal permissions.

        Parameters
        ----------
        this_path : Union[Path, List[Path]]
            A single Path object or a list of Path objects representing file(s).

        Returns
        -------
        Dict[str, dict]
            A dictionary where each key is the filepath and each value is a
            dictionary of file details.

        """

        def get_file_info(this_path: Path) -> dict:
            info = {
                'filename': this_path.name,
                'filepath': str(this_path),
                'size_bytes': this_path.stat().st_size,
                'create_at': Builder.time_to_dt(this_path.stat().st_birthtime),
                'modify_at': Builder.time_to_dt(this_path.stat().st_mtime),
                'octal_permission': oct(this_path.stat().st_mode)[-4:]
            }

            self.ctrl_log.debug(
                "File information retrieved: %s",
                info
            )
            
            return info
        
        if isinstance(this_path, Path):
            this_path = [this_path]

        if isinstance(self.base_path, Path):
            this_path = [self.base_path.joinpath(path) for path in this_path]

        file_info_dict = {}
        for path in this_path:
            if not path.is_file():
                raise FileNotFoundError(
                    f"The path {path} does not point to a valid file."
                )
            
            file_info_dict[str(path)] = get_file_info(path)

        self.ctrl_log.debug(
            "Information retrieved for %s files.",
            len(file_info_dict))

        return file_info_dict


    @ensure_path
    def copy_directory(self,
                       this_path: Path,
                       that_path: Path
                       ) -> None:
        """
        Copies the entire directory specified by 'this_path' to a new location
        specified by 'that_path'. If 'that_path' does not exist, it will be
        created. All contents of the directory including files and
        subdirectories will be copied.

        This function includes a check to prevent cyclic copies by ensuring that
        'that_path' is not a subdirectory of 'this_path'.

        Parameters
        ----------
        this_path : Path
            The path of the source directory to be copied.
        that_path : Path
            The path of the destination directory where 'this_path' will be
            copied to.

        Note
        ----
        The function prevents cyclic copies where 'that_path' is within
        'this_path' to avoid infinite recursion.
        """

        self.ctrl_log.debug(
            "Attempting to copy directory from %s to %s.",
            this_path, that_path
        )

        """ Check for cyclic copy """
        if that_path.resolve().is_relative_to(this_path.resolve()):
            raise ValueError(
                "Cannot copy a directory into itself or its subdirectories."
            )

        """ Ensure the source directory exists """
        if not this_path.is_dir():
            raise FileNotFoundError(
                f"The source directory '{this_path}' was not found."
            )

        self.ensure_directory(this_path = that_path)
    
        for item in this_path.iterdir():
            dest_path = that_path / item.name
            if item.is_dir():
                self.ctrl_log.debug(
                    "Recursively copying subdirectory %s to %s.",
                    item, dest_path
                )
                        
                Builder.copy_directory(item, dest_path)

            else:
                self.ctrl_log.debug(
                    f"Copying %s to %s.", 
                    item, dest_path
                )

                shutil.copy2(item, dest_path)


    @ensure_path
    def move_directory(self,
                       this_path: Path, 
                       that_path: Path
                       ) -> None:
        """
        Moves the entire directory specified by 'this_path' to a new location
        specified by 'that_path'. If 'that_path' does not exist, it will be
        created. All contents of the directory including files and
        subdirectories will be moved.

        This function includes a check to prevent cyclic moves by ensuring that
        'that_path' is not a subdirectory of 'this_path'.

        Parameters
        ----------
        this_path : Path
            The path of the source directory to be moved.
        that_path : Path
            The path of the destination directory where 'this_path' will be
            moved to.

        Note
        ----
        The function prevents cyclic moves where 'that_path' is within
        'this_path' to avoid infinite recursion.
        """

        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)
            that_path = self.base_path.joinpath(that_path)

        """ Check for cyclic move """
        if that_path.resolve().is_relative_to(this_path.resolve()):
            raise ValueError(
                "Cannot move a directory into itself or its subdirectories."
            )

        self.ctrl_log.debug(
            f"Copying %s to %s.", 
            this_path, that_path
        )
        
        shutil.move(str(this_path), str(that_path))


    @ensure_path
    def compare_directories(self,
                            this_path: Path,
                            that_path: Path
                            ) -> dict:

        """
        Compares the contents of two directories and identifies the differences.

        This function compares the files present in both directories specified
        by 'this_path' and 'that_path', and identifies unique files in each
        directory as well as common files with differences in content.

        Parameters
        ----------
        this_path : Path
            The path of the first directory to compare.
        that_path : Path
            The path of the second directory to compare.

        Returns
        -------
        dict
            A dictionary containing information about the comparison results,
            including unique files in 'this_path', unique files in 'that_path',
            and common files with differences in content. The dictionary
            structure is as follows:

            {
                'unique_this_path': List[Path],
                'unique_that_path': List[Path],
                'differences': List[Dict[str, Union[str, int]]]
            }

        """
        
        if isinstance(self.base_path, Path):
            this_path = self.base_path.joinpath(this_path)
            that_path = self.base_path.joinpath(that_path)

        self.ctrl_log.debug(
            "Comparing directories: %s and %s",
            this_path, that_path
        )

        if not this_path.is_dir() or not that_path.is_dir():
            raise ValueError("Both paths must be directories.")


        """ Find all files in both directories """
        this_files: set[Path] = set(
            Builder.find_files_by_name(
                this_path,
                hint = '',
                deep_search = True,
                is_hint_regex = False
            )
        )

        that_files: set[Path] = set(
            Builder.find_files_by_name(
                that_path,
                hint = '',
                deep_search = True,
                is_hint_regex = False
            )
        )

        """ Normalize paths to make them comparable """
        this_files_normalized = {
            file.relative_to(this_path)
            for file in this_files
        }

        that_files_normalized = {
            file.relative_to(that_path)
            for file in that_files
        }

        """ Identify unique and common files """
        unique_this = this_files_normalized - that_files_normalized
        unique_that = that_files_normalized - this_files_normalized
        common_files = this_files_normalized & that_files_normalized

        """ Prepare results dictionary """
        results: Dict[
            str,
            Union[List[Path], List[Dict[str, Union[str, int]]]]
            ] = {
                'unique_this_path': list(unique_this),
                'unique_that_path': list(unique_that),
                'differences': []
            }


        if unique_this:
            self.ctrl_log.debug(
                "Unique files in %s: %s",
                this_path, unique_this
            )

        if unique_that:
            self.ctrl_log.debug(
                "Unique files in %s: %s",
                that_path, unique_that
            )


        """ For common files, check for differences """
        for file in common_files:
            this_file_info = Builder.file_information(this_path / file).get(
                str(this_path / file), {})
            
            that_file_info = Builder.file_information(that_path / file).get(
                str(that_path / file), {})

            """ Check if there are any differences """
            differences = {
                key: this_file_info[key]
                for key in this_file_info
                if this_file_info.get(key) != that_file_info.get(key)
            }

            if differences:
                results['differences'].append({
                    'file': str(file),
                    'differences': differences
                })

                self.ctrl_log.debug(
                    "Differences found in file %s: %s",
                    file, differences
                )

        return results
    