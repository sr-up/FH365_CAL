#  Copyright (c) 2021. fit&healthy 365

import mysql.connector

from abc import ABC, abstractmethod

from Tools import flatten


class ConnectError(Exception):
    pass


class CredentialError(Exception):
    pass


class SQLError(Exception):
    pass


class UseDatabase(ABC):
    """ABC (Abstract Base Class) Context Manager that handles connecting to and entering database context"""

    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self):
        try:
            self.access = mysql.connector.connect(**self.configuration)
            self.cursor = self.access.cursor()
            return self.cursor
        except mysql.connector.InterfaceError as err:
            raise ConnectError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialError(err)

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ConnectDatabase(UseDatabase):
    """used for non-commit transactions, does not protect against explicit commit() calls"""

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.access.rollback()
        self.cursor.close()
        self.access.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError
        elif exc_type:
            raise exc_type(exc_val)


class BeginDatabase(UseDatabase):
    """used for commit transactions"""

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.access.commit()
        self.cursor.close()
        self.access.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError
        elif exc_type:
            raise exc_type(exc_val)


class Connector:
    def __init__(self, config):
        self._config = config

    def fetch_challenge_header(self, cid: int) -> tuple:
        with ConnectDatabase(self._config) as cursor:
            _SQL = 'SELECT name, description FROM challenge WHERE id = %s'
            cursor.execute(_SQL, (cid,))
            return cursor.fetchone()

    def fetch_challenge_habits(self, uid: int, cid: int) -> tuple:
        with ConnectDatabase(self._config) as cursor:
            _SQL = 'SELECT habit1, habit2 ' \
                   'FROM person_challenge ' \
                   'WHERE person_id = %s AND challenge_id = %s'
            cursor.execute(_SQL, (uid, cid))
            return cursor.fetchone()

    def fetch_challenge_events(self, uid: int, cid: int) -> list:
        with ConnectDatabase(self._config) as cursor:
            _SQL = 'SELECT event_date ' \
                   'FROM challenge_event ' \
                   'WHERE person_id = %s AND challenge_id = %s'
            cursor.execute(_SQL, (uid, cid))
            rows = cursor.fetchall()
            dates = flatten(rows)
            return dates

    def delete_challenge_event(self, uid: int, cid: int, date: str):
        with BeginDatabase(self._config) as cursor:
            _SQL = 'DELETE FROM challenge_event ' \
                   'WHERE person_id = %s' \
                   ' AND challenge_id = %s' \
                   ' AND event_date = %s'
            cursor.execute(_SQL, (uid, cid, date))

    def insert_challenge_event(self, uid: int, cid: int, date: str):
        with BeginDatabase(self._config) as cursor:
            _SQL = 'INSERT INTO challenge_event ' \
                   '(person_id, challenge_id, event_date)' \
                   'VALUES (%s, %s , %s)'
            cursor.execute(_SQL, (uid, cid, date))
