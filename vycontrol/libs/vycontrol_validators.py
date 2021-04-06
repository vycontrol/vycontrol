import validators
from validators.utils import *
import re
from password_strength import PasswordPolicy


@validator
def validator_letters_numbers(value):
    if re.match("^[A-Za-z0-9]*$", value):
        return True

@validator
def validator_group(value):
    if re.match("^[A-Za-z0-9\.\-_]*$", value):
        return True
       
@validator
def validator_ipv4_cidr(value):
    if re.match("^(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?$", value):
        return True

@validator
def validator_password(value):
    policy = PasswordPolicy.from_names(
        length=8,  # min length: 8
        uppercase=1,  # need min. 2 uppercase letters
        numbers=1,  # need min. 2 digits
        special=1,  # need min. 2 special characters
    )
    if len(policy.test(value)) == 0:
        return True
