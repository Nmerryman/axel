from mysql.connector import connect, Error
from mysql.connector.connection_cext import CMySQLConnection as Conn
from mysql.connector.cursor_cext import CMySQLCursor as Curs
from dotenv import load_dotenv
import os

"""
The intent of this file to isolate database operations and keep the rest of the system more modular
This module will handle all database contexts for me
"""


# partially for typing reasons
connection: Conn  # reuse connection (prob more efficient)
cursor: Curs


def load_connection():
    """
    Load the initial connection to set the global connection. Does NOT use a database, it must be done manually
    :return: Bool whether it works or not
    """
    global connection, cursor
    connection = connect(host="localhost", user=os.environ.get("dbUser"), password=os.environ.get("dbPass"))
    cursor = connection.cursor()


def execute_basic(command, list_data=None):
    """
    A simple primitive to execute commands
    :param command: String w/ command
    :param list_data: If set, use an alternative method to
    :return: None
    """
    global cursor
    # Consider extracting due to repetition
    if not list_data:
        cursor.execute(command)
    else:
        cursor.executemany(command, list_data)


def execute_commit(command, list_data=None):
    """
    Turn setting data into a 1 liner
    :param command: Passed to execute_basic
    :param list_data: Passed to execute_basic
    :return: None
    """
    global connection
    execute_basic(command, list_data)
    connection.commit()


def execute_fetch(command):
    """
    Turn getting data into a 1 liner
    :param command: Passed to execute_basic
    :return: None
    """
    global cursor
    execute_basic(command)
    return cursor.fetchall()


def ensure_setup():
    """
    Checks to make sure that all of the database + tables is set up correctly and ready to use
    :return: None
    """

    execute_basic("CREATE DATABASE IF NOT EXISTS axel_data")
    execute_basic("use axel_data")
    create_users_table = """
    create table if not exists users(
        id int auto_increment primary key,
        username varchar(100)
    )
    """

    create_file_instance_table = """
    create table if not exists files(
        id int auto_increment primary key,
        owner int,
        foreign key(owner) references users(id),
        hash varchar(32),
        is_alive bool
    )
    """
    # TODO make sure the hash has an appropriate amount of space

    create_user_uploads_table = """
    create table if not exists posts(
        id int auto_increment primary key,
        poster int,
        foreign key(poster) references users(id),
        used_instance int,
        foreign key(used_instance) references files(id),
        time int
    )
    """

    execute_commit(create_users_table)
    execute_commit(create_file_instance_table)
    execute_commit(create_user_uploads_table)


# We may want to do some of this in a different file
load_dotenv()
load_connection()
ensure_setup()

if __name__ == '__main__':

    print(execute_fetch("show tables"))
    print(execute_fetch("describe files"))
    print(execute_fetch("describe posts"))
    print(execute_fetch("describe users"))
