import functools
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.databases import mysql
from sqlalchemy import String, Unicode


def use_session(f):
    """ Wrapper around `SQLiteBackend.use_session()` for code simplicity. """
    def wrapper(self, *args, **kwargs):
        try:
            result = self.use_session(f)(self, *args, **kwargs)
            return result
        except Exception:
            raise
    return wrapper


def create_declarative_base():
    base = declarative_base()
    return base


class SQLiteBackend(object):
    """ The SQLite backend that manages database connections, sessions
    and bootstraping. """

    def __init__(self, db_string, base):
        if db_string:
            self.engine = None
            self.Base = base
            self.Session = sessionmaker(
                autocommit=False,
                expire_on_commit=False
            )
            self.setup_session(db_string)

    def use_session(self, f):
        """ Creates and manages sessions for simple database operations. """
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            session = self.Session()
            try:
                return f(args[0], session, *(args[1:]), **kwargs)
            except:
                session.rollback()
                raise
            finally:
                session.expunge_all()
                session.close()
        return wrapper

    def _create_engine(self, db_string=None):
        if self.engine:
            return
        self.engine = create_engine(db_string, echo=False, pool_recycle=3600)

    def setup_session(self, db_string=None):
        self._create_engine(db_string)
        self.Session.configure(bind=self.engine)

    def reset(self):
        self.Base.metadata.drop_all(bind=self.engine)
        self.Base.metadata.create_all(bind=self.engine)

    def ping(self):
        session = self.Session()
        pong = session.execute('select 1').fetchall()
        session.close()
        return pong

    def bootstrap(self):
        """ Does bootstraping i.e. creates database and tables.
        Assumes no databases have been setup. Retries until connection is
        established.
        """
        url = self.engine.url
        engine = create_engine(str(url))
        connection = None
        for i in range(10):  # retries
            try:
                connection = engine.connect()
            except:
                print "DBServer is probably not up yet, Retrying ..."
                time.sleep(i * 5)
                continue
        if not connection:
            raise Exception("Couldn't connect to DBServer even after retries!")

        self.Base.metadata.create_all(bind=self.engine)
        connection.close()
