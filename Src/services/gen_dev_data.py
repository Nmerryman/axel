from .data_structures import FileToken
from faker import Faker


"""
The structure I try to go for is to a default and randomized option
"""


fake = Faker()


def file_token_default():
    return FileToken('a', 'b', 'c', 1)


def file_token_random():
    return FileToken(fake.file_name(), fake.sha256(), fake.uuid4(), fake.unix_time())


