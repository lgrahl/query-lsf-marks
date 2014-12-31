#!/usr/bin/env python3
"""
query-lsf-marks
***************

.. moduleauthor:: Lennart Grahl <lennart.grahl@gmail.com>

Query the LSF (also known as `qis server`) and show a desktop
notification on changes to your marks.
"""

__author__ = 'Lennart Grahl <lennart.grahl@gmail.com>'
__status__ = 'Development'
__version__ = '0.1.2'

import sys
import time
import getpass

import requests
import keyring

from bs4 import BeautifulSoup, SoupStrainer
from zwnflibs import logging
from zwnflibs.logging.handler.file import RotatingFileHandler
from zwnflibs.logging.handler import StreamHandler
from zwnfqan import Client, QANError, QueryError, HandlerError
from zwnfqan.query import Query
from zwnfqan.handler import Handler
from zwnfqan.notifier import ZwnfNotifier

# Setup logging
_service = 'query-lsf'
_log_format = '{asctime} {module:^14} {levelname:<17} {message}'
_date_format = '%Y-%m-%d %H:%M:%S'
_formatter = logging.Formatter(fmt=_log_format, datefmt=_date_format, style='{')
_logger = logging.get_logger(_service)
_logger.set_level(logging.DEBUG)
_handler = StreamHandler()
_handler.set_level(logging.INFO)
_handler.set_formatter(_formatter)
_logger.add_handler(_handler)
_handler = RotatingFileHandler('{}.log'.format(_service), max_bytes=100000, backup_count=1)
_handler.set_formatter(_formatter)
_logger.add_handler(_handler)


class FHMarksOverviewHandler(Handler):
    """
    Retrieve and notify changes to marks from the LSF.
    """
    def filter(self, obj):
        """Return the marks overview table text."""
        tables = SoupStrainer('table')
        soup = BeautifulSoup(obj.text, 'html.parser', parse_only=tables)
        try:
            _, marks = soup.find_all('table')
            data = []
            # Iterate over table rows
            for row in marks.find_all('tr'):
                # Select these bold columns
                cols = row.find_all('td', 'qis_konto')
                if not cols:
                    continue
                # We're only interested in the trimmed text
                cols = (tag.get_text().strip() for tag in cols)
                # Ignore uninteresting columns
                id_, name, _, mark, _, status, *_ = cols
                # Append to the data list
                data.append((id_, name, status, mark))
        except ValueError as exc:
            raise HandlerError("Couldn't extract table with marks") from exc
        return data

    def compare(self, current, new):
        """
        Compare the current with the new overview table and return
        the difference.
        """
        diff = list(set(new) - set(current))
        diff.sort(key=lambda row: row[0])
        return diff

    def prepare(self, obj):
        """Return the exam name, mark (if any) and status."""
        rows = ('{}: {}{}'.format(name, status, ' ({})'.format(mark) if mark else '')
                for _, name, status, mark in obj)
        return '\n'.join(rows)


class FHMarksOverviewQuery(Query):
    def __init__(self, username, password, timeout=90):
        super().__init__()
        self._username = username
        self._password = password
        self._timeout = timeout

    def send(self):
        try:
            session = requests.Session()
            _logger.debug('New session: {}', session)
            # Get jsessionid
            url = 'https://lsf.fh-muenster.de/qisserver/rds?state=user&type=0'
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser',
                                 parse_only=SoupStrainer('form'))
            url = soup.find('form').get('action')
            _logger.debug('Retrieved jsessionid: {}', url)

            # Login
            _logger.debug('Sending login data for user "{}"', self._username)
            response = session.post(url, data={
                'asdf': self._username,
                'fdsa': self._password,
            }, timeout=self._timeout)

            # Check for login error
            if 'Anmeldung fehlgeschlagen!' in response.text:
                raise QueryError('Username or password wrong')
            _logger.debug('Login successful')

            # Get asi (whatever that is)
            s = '&amp;asi='
            start = response.text.index('&amp;asi=') + len(s)
            asi = response.text[start:start+20]
            _logger.debug('ASI: {}', asi)
            url = 'https://lsf.fh-muenster.de/qisserver/rds?state=notenspiegelStu' \
                  'dent&next=list.vm&nextdir=qispos/notenspiegel/student&createIn' \
                  'fos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabsc' \
                  'hl%3D84%2Cstgnr%3D1%7Cstudiengang%3Astg%3D409&expand=0&asi={}#' \
                  'auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1%7Cstudiengan' \
                  'g%3Astg%3D409'.format(asi)
            _logger.debug('Marks URL: {}', url)

            # Now retrieve the marks overview
            _logger.debug('Fetching marks...')
            response = session.get(url, timeout=self._timeout)
            _logger.debug('... marks fetched.')
            return response
        except QANError:
            raise
        except BaseException as exc:
            raise QueryError("Couldn't query LSF") from exc


def main():
    # Parameters
    if len(sys.argv) != 3:
        print('Usage: query-lsf.py <username> <interval>')
        sys.exit(1)

    # Request password if none set
    username, interval = sys.argv[1:3]
    interval = int(interval)
    password = keyring.get_password(_service, username)
    if password is None:
        password = getpass.getpass('Password for "{}": '.format(username))
        keyring.set_password(_service, username, password)

    # Setup client
    _logger.debug('Setting up classes')
    query = FHMarksOverviewQuery(username, password)
    handler = FHMarksOverviewHandler()
    notifier = ZwnfNotifier('LSF', title='Update', timeout=0)
    _logger.debug('Instances: {}, {}, {}', query, handler, notifier)

    # Loop forever
    try:
        client = Client(query, handler, notifier, path='{}.pickle'.format(_service))
        _logger.debug('Created client: {}', client)
        while True:
            _logger.info('Querying LSF...')
            try:
                client.run()
            except QANError as exc:
                _logger.exception(exc)
            _logger.info('... done!')
            _logger.debug('Sleeping for {} minutes...', interval)
            time.sleep(interval * 60)
    except KeyboardInterrupt as exc:
        sys.exit(0)
    except Exception:
        print('Exiting due to error:')
        raise
        
if __name__ == '__main__':
    main()
