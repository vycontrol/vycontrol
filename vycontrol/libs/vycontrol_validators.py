import validators
from validators.utils import *
import re


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