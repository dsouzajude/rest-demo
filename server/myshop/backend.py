import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import Column, Boolean, DateTime, TIMESTAMP, Integer, String
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql.expression import desc

import sql, utils, errors


Base = sql.create_declarative_base()


class User(Base):

    __tablename__ = 'users'

    username = Column(String(32), primary_key=True)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(32), nullable=False, index=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys if k != 'hashed_password'}

    def to_json_dict(self):
        d = self.to_dict()
        d['create_time'] = utils.format_datetime(d['create_time'])
        d['update_time'] = utils.format_datetime(d['update_time'])
        return d


class UserLogin(Base):

    __tablename__ = 'user_logins'

    username = Column(String(32), primary_key=True, nullable=False)
    login_time = Column(DateTime, primary_key=True, default=datetime.utcnow)

    # if session_token is null, indicates login failure
    session_token = Column(String(128), index=True, unique=True)

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys if k!= 'session_token'}

    def to_json_dict(self):
        d = self.to_dict()
        d['login_time'] = utils.format_datetime(d['login_time'])
        return d


class UserSession(Base):

    __tablename__ = 'user_sessions'

    session_token = Column(String(128), primary_key=True, nullable=False)
    username = Column(String(32), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        keys = self.__table__.c.keys()
        return {k: getattr(self, k) for k in keys}

    def to_json_dict(self):
        d = self.to_dict()
        d['create_time'] = utils.format_datetime(d['create_time'])
        return d


class MyshopBackend(sql.SQLiteBackend):
    def __init__(self, db_url):
        super(MyshopBackend, self).__init__(db_url, Base)

    @sql.use_session
    def reset(self, session):
        super(MyshopBackend, self).reset()

    @sql.use_session
    def create_user(self, session, username, hashed_password, full_name):
        """ Inserts a new user into the database. """
        user = User(
            username=username,
            hashed_password=hashed_password,
            full_name=full_name
        )
        session.add(user)
        try:
            session.commit()
            return user
        except IntegrityError:
            session.rollback()
            raise errors.UserExists("username={}".format(username))

    @sql.use_session
    def get_user(self, session, username):
        user = session.query(User).filter_by(username=username).first()
        return user

    @sql.use_session
    def insert_login_attempt(self, session, username, session_token):
        user_login = UserLogin(username=username, session_token=session_token)
        session.add(user_login)
        session.commit()
        return user_login

    @sql.use_session
    def create_session(self, session, session_token, username):
        user_session = UserSession(
            session_token=session_token,
            username=username
        )
        session.add(user_session)
        session.commit()
        return user_session

    @sql.use_session
    def get_session(self, session, session_token):
        user_session = session.query(UserSession) \
                        .filter_by(session_token=session_token) \
                        .first()
        return user_session

    @sql.use_session
    def get_successful_logins(self, session, username, max_records):
        user_logins = session.query(UserLogin) \
                             .filter(UserLogin.username == username) \
                             .filter(UserLogin.session_token != None) \
                             .order_by(desc(UserLogin.login_time)) \
                             .limit(max_records) \
                             .all()
        return user_logins
