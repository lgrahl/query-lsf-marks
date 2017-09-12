import ast
import os
import sys

from setuptools import (
    setup,
    find_packages,
)


def get_version():
    path = os.path.join(os.path.dirname(__file__), 'query_lsf', '__init__.py')
    with open(path) as file:
        for line in file:
            if line.startswith('__version__'):
                _, value = line.split('=', maxsplit=1)
                return ast.literal_eval(value.strip())
        else:
            raise Exception('Version not found in {}'.format(path))


# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Check python version
py_version = sys.version_info[:2]
if py_version < (3, 4):
    raise Exception('This project requires Python >= 3.4')

# Development requirements
# Note: These are just tools that aren't required, so a version range
#       is not necessary here.
dev_require = [
    'flake8>=3.3.0',
    'isort>=4.2.5',
]

setup(
    name='query-lsf',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.6.0,<5',
        'keyring>=10.4.0,<11',
        'logbook>=1.1.0,<2',
        'requests>=2.18.4,<3',
    ],
    tests_require=dev_require,
    extras_require={
        'dev': dev_require,
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'query-lsf = query_lsf.__main__:main',
        ],
    },

    # PyPI metadata
    author='Lennart Grahl',
    author_email='lennart.grahl@gmail.com',
    description='Query the FH-Münster LSF for (new) marks.',
    license='MIT',
    keywords='fh-muenster muenster marks lsf',
    url='https://github.com/lgrahl/query-lsf-marks',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
    ],
)
