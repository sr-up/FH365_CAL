#  Copyright (c) 2021. fit&healthy 365

import mysql.connector

from abc import ABC, abstractmethod


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
    def __exit__(self, exc_type, exc_val, exc_tb) -> 'cursor': pass


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
