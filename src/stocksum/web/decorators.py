from contextlib import contextmanager
from stocksum.web.connections import database

@contextmanager
def new_session():
    '''
    Creates a new session, remembers to close and rollsback
    if the session fails.

    Usage:

        with new_session() as session:
            session.add(some_model())
    '''
    s = database.session()
    try:
        yield s
    except:
        raise
    finally:
        s.close()