#!/usr/bin/env python3
"""
query-lsf-marks
***************

.. moduleauthor:: Lennart Grahl <lennart.grahl@gmail.com>

Query the LSF (also known as `qis server`) and show a desktop
notification on changes to your marks.
"""

import json

import requests

# noinspection PyPackageRequirements
from bs4 import (
    BeautifulSoup,
    SoupStrainer,
)
from logbook import (
    Logger,
)

from .notify import (
    Notification,
)

__author__ = 'Lennart Grahl <lennart.grahl@gmail.com>'
__status__ = 'Development'
__version__ = '0.2.0'

SERVICE_NAME = 'query-lsf'
DEFAULT_STORAGE_PATH = '.query-lsf-marks.json'


def notify_marks(difference):
    # Format new entries (exam name, mark (if any), status)
    rows = ('{}: {}{}'.format(name, status, ' ({})'.format(mark) if mark else '')
            for _, name, status, mark in difference)
    rows = '\n'.join(rows)

    # Notify
    Notification(title='LSF Marks', message=rows, timeout=10).show()


def set_storage_data(path, rows):
    log = Logger('lsf.storage')
    with open(path, 'w') as file:
        json.dump(rows, file)
        log.debug('Storage updated')


def compare_marks(current, new):
    diff = list(set(new) - set(current))
    diff.sort(key=lambda row: row[0])
    return diff


def get_storage_data(path):
    log = Logger('lsf.storage')
    try:
        with open(path, 'r') as file:
            rows = json.load(file)
            log.debug('Storage loaded')
    except FileNotFoundError:
        log.info('Storage not found, creating')
        rows = []
    except json.JSONDecodeError:
        log.warning('Storage corrupted, re-creating')
        rows = []
    return [tuple(entry) for entry in rows]


def filter_marks(response):
    tables = SoupStrainer('table')
    soup = BeautifulSoup(response.text, 'html.parser', parse_only=tables)
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
        id_, name, mark, _, status, *_ = cols
        # Append to the data list
        data.append((id_, name, status, mark))

    return data


def query_marks_overview(username, password, timeout=90):
    log = Logger('lsf.query')
    session = requests.Session()
    log.debug('New session: {}', session)

    # Get jsessionid
    url = 'https://lsf.fh-muenster.de/qisserver/rds?state=user&type=0'
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser',
                         parse_only=SoupStrainer('form'))
    url = soup.find('form').get('action')
    log.debug('Retrieved jsessionid: {}', url)

    # Login
    log.debug('Sending login data for user "{}"', username)
    response = session.post(url, data={
        'asdf': username,
        'fdsa': password,
    }, timeout=timeout)

    # Check for login error
    if 'Anmeldung fehlgeschlagen!' in response.text:
        raise ValueError('Username or password wrong')
    log.debug('Login successful')

    # Get asi (whatever that is)
    s = '&amp;asi='
    start = response.text.index('&amp;asi=') + len(s)
    asi = response.text[start:start+20]
    log.debug('ASI: {}', asi)
    url = 'https://lsf.fh-muenster.de/qisserver/rds?state=notenspiegelStu' \
          'dent&next=list.vm&nextdir=qispos/notenspiegel/student&createIn' \
          'fos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabsc' \
          'hl%3D90%2Cstgnr%3D1%7Cstudiengang%3Astg%3D409&expand=0&asi={}'.format(asi)
    log.debug('Marks URL: {}', url)

    # Now retrieve the marks overview
    log.debug('Fetching marks...')
    response = session.get(url, timeout=timeout)
    log.debug('... marks fetched.')
    return response


def query_once(path, username, password):
    log = Logger('lsf')

    # Request and filter marks
    response = query_marks_overview(username, password)
    new = filter_marks(response)
    log.trace('New data: {}', new)

    # Get storage data
    current = get_storage_data(path)
    log.trace('Current data: {}', current)

    # Compare with storage
    difference = compare_marks(current, new)
    if difference:
        log.trace('Difference: {}', difference)

        # Store data
        set_storage_data(path, new)

        # Notify
        notify_marks(difference)
