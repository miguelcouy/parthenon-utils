from os import PathLike
from shutil import copytree, copy2
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, List, Iterable
import zipfile
import tarfile

class Zipper:
    @staticmethod
    def create_backup(target: Union[Path, PathLike], 
                      compress_format: Optional[str] = None
                      ) -> Path:
        """
        Creates a backup of the specified file or directory. The backup can be
        optionally compressed into a .zip format. If compression is not 
        requested, the file or directory is simply copied with a timestamp 
        appended to its name.

        Parameters:
        - target (Union[str, Path]): The file or directory to be backed up. 
        This is a relative path from the base_directory of the controller 
        object.
        - compress_format (Optional[str]): Specifies the compression format to
        be used for the backup. Currently, only 'zip' format is supported. If 
        None, the backup will not be compressed. Defaults to None.

        Returns:
        - Path: The path to the created backup file or directory.

        Raises:
        - FileNotFoundError: If the target file or directory does not exist.

        The method first checks if the target exists. If it does not, a 
        FileNotFoundError is raised. It then proceeds to create a backup name 
        that includes a timestamp for uniqueness. If a compression format is 
        specified, the 'manage_compressed_files' method is used to create a 
        compressed backup. Otherwise, the file or directory is simply copied to
        the backup location.

        Example Usage:
        >>> controller = Controller(base_directory='/path/to/base')
        >>> backup_path = controller.create_backup(
                target='important_docs',
                compress_format='zip'
            )
        >>> print(backup_path)
        /path/to/base/important_docs_20240318120000.zip
        """

        if not target.exists():
            raise FileNotFoundError(
                f"Target {target} does not exist and cannot be backed up."
            )

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_name = (
            f"{target.stem}_{timestamp}" 
            + (
                f".{compress_format}" 
                if compress_format 
                else target.suffix
            )
        )
        backup_path = target.parent.joinpath(backup_name)

        if target.is_dir():
            if compress_format:
                Zipper.manage_compressed_files(
                    action = 'create', 
                    source = target, 
                    destination = backup_path
                )

            else:
                copytree(
                    src = target, 
                    dst = backup_path
                )
                
        else:
            if compress_format:
                with zipfile.ZipFile(backup_path, mode = 'w') as zipf:
                    zipf.write(
                        filename = target, 
                        arcname = target.name
                    )

            else:
                copy2(
                    src = target, 
                    dst = backup_path
                )

        return backup_path
    
    @staticmethod
    def manage_compressed_files(action: str, 
                                source: Union[str, Path], 
                                destination: Union[str, Path] = None, 
                                files: List[Union[str, Path]] = None
                                ) -> None:
        """
        Manages compressed files by performing specified actions such as 
        creating archives, extracting files, or adding files to existing 
        archives.

        Parameters:
        - action (str): The action to be performed. Supported actions are 
        'create', 'extract', and 'add'.
        - source (Union[str, Path]): The source file or directory path for the 
        action.
        - destination (Union[str, Path], optional): The destination file or 
        directory path. Required for 'create' and 'add' actions.
        - files (List[Union[str, Path]], optional): A list of files to be added 
        to the compressed archive. Required for 'add' action.

        Raises:
        - ValueError: If an unsupported action is specified.
        
        The method supports three actions:
        - 'create': Creates a compressed archive (.zip or .tar.gz) from the 
        specified source directory or file. The format is determined by the 
        destination's file extension.
        - 'extract': Extracts files from a compressed archive to the specified 
        destination directory. Ensures safe extraction to prevent directory 
        traversal attacks.
        - 'add': Adds specified files to an existing compressed archive. The 
        archive's format is determined by its file extension.

        Example Usage:
        >>> controller = Controller()
        >>> controller.manage_compressed_files(
                action='create',
                source='/path/to/source',
                destination='/path/to/destination/archive.zip'
            )
        >>> controller.manage_compressed_files(
                action='extract',
                source='/path/to/archive.zip',
                destination='/path/to/extracted_files'
            )
        >>> controller.manage_compressed_files(
                action='add',
                source='/path/to/archive.zip',
                files=['/path/to/file1.txt', '/path/to/file2.txt']
            )
        """

        if action not in ['create', 'extract', 'add']:
            raise ValueError(
                f"Unsupported action '{action}'."
                +  "Supported actions are 'create', 'extract', 'add'."
            )

        if action == 'create':
            if destination.suffix == '.zip':
                with zipfile.ZipFile(destination, mode = 'w') as zipf:
                    for file in Path(source).rglob('*'):
                        zipf.write(
                            filename = file, 
                            arcname = file.relative_to(source)
                        )

            elif destination.suffix.isin(['.tar.gz' , '.tar']):
                with tarfile.open(destination, 'w:gz') as tar:
                    tar.add(source, arcname='.')

        elif action == 'extract':
            if source.suffix == '.zip':
                with zipfile.ZipFile(source, mode = 'r') as zipf:
                    zipf.extractall(
                        path = destination
                    )
                    
            elif source.suffix.isin(['.tar.gz' , '.tar']):
                with tarfile.open(source, mode = 'r:gz') as tar:
                    def safe_filter(members: Iterable[tarfile.TarInfo]):
                        for member in members:
                            if (".." in member.name 
                                or member.name.startswith('/')
                                ):
                                continue
                            yield member

                    tar.extractall(destination, members = safe_filter(tar))
        
        elif action == 'add':
            if source.suffix == '.zip':
                with zipfile.ZipFile(source, mode = 'a') as zipf:
                    for file in files:
                        zipf.write(
                            filename = file, 
                            arcname = file.relative_to(Path(file).parent)
                        )
                        
            elif source.suffix.isin(['.tar.gz' , '.tar']):
                with tarfile.open(source, mode = 'a:gz') as tar:
                    for file in files:
                        tar.add(
                            name = file, 
                            arcname=Path(file).name
                        )