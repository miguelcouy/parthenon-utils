__author__ = 'Miguel Freire Couy'
__credits__ = ['Miguel Freire Couy']
__version__ = '0.0.1'
__maintainer__ = 'Miguel Freire Couy'
__email__ = 'miguel.couy@Ooutlook.com'
__status__ = 'Production'

from cryptography.fernet import Fernet, InvalidToken
from typing import Union, Optional
from functools import wraps
import base64
from pathlib import Path

from .nologger import NoLogger


class Encrypter:
    """
    A class for encrypting and decrypting strings using Fernet symmetric
    encryption.

    This class provides a convenient interface for the Fernet encryption scheme,
    which is a symmetric encryption method ensuring that data encrypted cannot
    be decrypted without the same key used for encryption.

    Attributes:
        key (Union[str, Fernet]):
            The encryption key as a str or Fernet object. If a str is provided,
            it is automatically converted to a Fernet object.

    Methods:
        decrypt(cipher_text: str) -> str:
            Decrypts the provided cipher text back into plain text.

        encrypt(plain_text: str) -> str:
            Encrypts the provided plain text into cipher text.

        generate_key() -> str:
            Generates a new Fernet key.
    """

    def __init__(self, 
                 key: Union[str, bytes, Fernet] = None,
                 ) -> None:
        
        self.key = key
        self.ctrl_log = NoLogger()
        self._initialize_key()

    def _initialize_key(self):
        """
        Initializes the encryption key. Validates and converts string or 
        bytes keys to Fernet objects, ensuring keys are of correct format and
        size.
        """
        
        if isinstance(self.key, (str, bytes)):
            self.key = Fernet(self.key)

        elif isinstance(self.key, Fernet):
            self.key = self.key

        else:
           raise TypeError(
               "The key must be a string, bytes, or a Fernet object."
            )

    @staticmethod
    def generate_key(as_bytes: bool = False) -> Union[str, bytes]:
        """
        Generates a new Fernet key and returns it either as a bytes object or a
        base64-encoded string.

        Parameters:
        -----------
        as_bytes : bool, optional
            Determines the format of the returned key. If True, returns the key
            as a bytes object. If False (default), returns the key as a
            base64-encoded string.

        Returns:
        --------
        Union[str, bytes]: The generated Fernet key in the specified format.
        """
        key = Fernet.generate_key()
        return (
            key
            if as_bytes
            else key.decode()
        )

    def decrypt(self, cipher_text: Union[str, bytes]) -> Union[str, bytes]:
        """
        Decrypts the provided cipher text back into plain text.

        Parameters:
            cipher_text (Union[str, bytes]): The cipher text to decrypt.

        Returns:
            Union[str, bytes]: The decrypted plain text in the same format as
            the input.

        Raises:
            cryptography.fernet.InvalidToken: If the cipher text cannot be
            decrypted.
        """

        is_input_str = isinstance(cipher_text, str)

        if is_input_str: cipher_text = cipher_text.encode()

        decrypted_bytes = self.key.decrypt(cipher_text)

        return (
            decrypted_bytes.decode()
            if is_input_str
            else decrypted_bytes
        )


    def encrypt(self, plain_text: Union[str, bytes]) -> Union[str, bytes]:
        """
        Encrypts the provided plain text into cipher text.

        Parameters:
            plain_text (Union[str, bytes]): The plain text to encrypt. Can be a
            string or bytes.

        Returns:
            Union[str, bytes]: The resulting cipher text in the same format as
            the input.
        """

        is_input_str = isinstance(plain_text, str)

        if is_input_str: plain_text = plain_text.encode()

        encrypted_bytes = self.key.encrypt(plain_text)

        return (
            encrypted_bytes.decode()
            if is_input_str
            else encrypted_bytes
        )

    @staticmethod
    def is_valid_key(key: Union[str, bytes]) -> bool:
        """
        Determines whether the provided key is a valid Fernet key by checking
        its format and length.

        A valid Fernet key must be a URL-safe base64-encoded 32-byte string.
        This method attempts to decode the key from base64 format and verifies
        that it is exactly 32 bytes long. It accepts the key as either a
        base64-encoded string or as raw bytes.

        Parameters:
        ----------
        key : Union[str, bytes]
            The encryption key to be validated. The key can be provided as a
            base64-encoded string or as raw bytes. If provided as a string, the
            key is expected to be URL-safe base64-encoded.

        Returns:
        -------
        bool
            Returns True if the key is valid according to Fernet specifications,
            False otherwise.

        Examples:
        --------
        >>> valid_key = Fernet.generate_key()
        >>> Encrypter.is_valid_key(valid_key)
        True

        >>> invalid_key = b"short_key"
        >>> Encrypter.is_valid_key(invalid_key)
        False

        >>> valid_key_str = valid_key.decode()
        >>> Encrypter.is_valid_key(valid_key_str)
        True

        >>> invalid_key_str = "not_a_base64_encoded_string"
        >>> Encrypter.is_valid_key(invalid_key_str)
        False
        """

        try:
            if isinstance(key, str):
                key = base64.urlsafe_b64decode(key)

            if not isinstance(key, bytes) or len(key) != 32:
                return False

            return True

        except (ValueError, TypeError, base64.binascii.Error):
            return False


    def encrypt_file(self,
                     input_path: Path,
                     output_path: Path = None
                     ) -> None:
        """
        Encrypts the content of a given file and either saves it to a new file
        or overwrites the original file with the encrypted content.

        This method reads the content of the file specified by 'input_path',
        encrypts it using the current encryption key, and then writes the
        encrypted content to a file specified by 'output_path'. If 'output_path'
        is not provided, the method overwrites the original file with the
        encrypted content.

        Parameters:
        ----------
        input_path : str
            The path to the input file whose content is to be encrypted. The
            path should be absolute or relative to the current working
            directory.

        output_path : str, optional
            The path to the output file where the encrypted content will be
            saved. If not provided, the 'input_path' file will be overwritten
            with its encrypted content. This path should be absolute or relative
            to the current working directory.

        Returns:
        -------
        None

        Raises:
        ------
        FileNotFoundError:
            If the input file specified by 'input_path' does not exist.

        IOError:
            If there is an error reading from the input file or writing to the
            output file.

        Examples:
        --------
        >>> encrypter = Encrypter(key=Fernet.generate_key())
        >>> encrypter.encrypt_file('path/to/plain.txt', 'path/to/encrypted.txt')
        # This will encrypt the content of 'plain.txt' and save it to
        # 'encrypted.txt'.

        >>> encrypter.encrypt_file('path/to/plain.txt')
        # This will encrypt the content of 'plain.txt' and overwrite the
        # original file with encrypted content.
        """
        if not output_path: output_path = input_path

        try:
            with open(input_path, 'rb') as file:
                file_data = file.read()

            encrypted_data = self.encrypt(file_data)

            with open(output_path, 'wb') as file:
                file.write(encrypted_data)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Input file not found: {input_path}"
            ) from e

        except IOError as e:
            raise IOError(
                f"Error processing file: {e}"
            ) from e

    def decrypt_file(self,
                     input_path: Path,
                     output_path: Path = None
                     ) -> None:
        """
        Decrypts the content of a given file and either saves it to a new file
        or overwrites the original file with the decrypted content.

        This method reads the encrypted content of the file specified by
        'input_path', decrypts it using the current encryption key, and then
        writes the decrypted content to a file specified by 'output_path'.
        If 'output_path' is not provided, the method overwrites the original
        file with its decrypted content.

        Parameters:
        ----------
        input_path : Path
            The path to the input file whose content is to be decrypted. The
            path can be provided as a string or a pathlib.Path object.

        output_path : Path
            The path to the output file where the decrypted content will be
            saved. If not provided, the 'input_path' file will be overwritten
            with its decrypted content. This path can be provided as a string or
            a pathlib.Path object.

        Returns:
        -------
        None

        Raises:
        ------
        FileNotFoundError:
            If the input file specified by 'input_path' does not exist.

        IOError:
            If there is an error reading from the input file or writing to the
            output file.

        Examples:
        --------
        >>> encrypter = Encrypter(key=Fernet.generate_key())
        >>> encrypter.decrypt_file('path/to/encrypted.txt', 'path/to/plain.txt')
        # This will decrypt the content of 'encrypted.txt' and save it to
        # 'plain.txt'.

        >>> encrypter.decrypt_file('path/to/encrypted.txt')
        # This will decrypt the content of 'encrypted.txt' and overwrite the
        # original file with decrypted content.
        """
        if not output_path:
            output_path = input_path

        try:
            with open(input_path, 'rb') as file:
                encrypted_data = file.read()

            decrypted_data = self.decrypt(encrypted_data)

            with open(output_path, 'wb') as file:
                file.write(decrypted_data)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Input file not found: {input_path}"
            ) from e

        except IOError as e:
            raise IOError(
                f"Error processing file: {e}"
            ) from e