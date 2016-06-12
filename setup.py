from distutils.core import setup
from os import path

from setuptools import find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='rfc_reader',
    version='0.2',
    packages=find_packages(exclude=['tests']),
    # scripts=['rfc.py'],
    url='https://github.com/monsieurh/rfc_reader',
    license='GPL3',
    author='monsieur_h',
    author_email='ray.hubert@gmail.com',
    description='A tool to read and search through IETF RFC documents',
    long_description=long_description,
    keywords="RFC rfc IETF",
    platforms='any',
    entry_points={
        'console_scripts': [
            'rfc = rfc.rfc:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Debuggers',
    ]
)
