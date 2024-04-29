from setuptools import setup, find_packages


setup(
    name = 'parthenon_utils',
    version = '0.0.4',
    packages = find_packages(),
    install_requires = [
        'cryptography>=42.0.3'
    ]
)