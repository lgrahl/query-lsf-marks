import sys
import time
import getpass

import keyring

from logbook import (
    Logger,
    StderrHandler,
)
from .notify import (
    register,
)

from . import (
    SERVICE_NAME,
    DEFAULT_STORAGE_PATH,
    query_once,
)


def main():
    logging_handler = StderrHandler(level='DEBUG')
    with logging_handler.applicationbound():
        log = Logger('lsf')

        # Parameters
        if len(sys.argv) < 3:
            log.critical('Usage: query-lsf.py <username> <interval (seconds)> [storage]')
            sys.exit(1)
        path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_STORAGE_PATH

        # Register notification
        register(SERVICE_NAME)

        # Request password if none set
        username, interval = sys.argv[1:3]
        interval = int(interval)
        password = keyring.get_password(SERVICE_NAME, username)
        if password is None:
            password = getpass.getpass('Password for "{}": '.format(username))
            keyring.set_password(SERVICE_NAME, username, password)

        # Loop forever
        try:

            while True:
                log.info('Querying LSF...')
                try:
                    query_once(path, username, password)
                except BaseException as exc:
                    log.exception(exc)
                log.info('... done!')
                log.debug('Sleeping for {} minutes...', interval)
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            log.critical('Exiting due to exception')
            raise

if __name__ == "__main__":
    main()
