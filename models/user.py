#!/usr/bin/env python3
"""User class"""
from models.base_model import BaseModel


class User(BaseModel):
    """Creates a user object"""

    email = ""
    password = ""
    first_name = ""
    last_name = ""

