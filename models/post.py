#!/usr/bin/env python3
"""Post Class"""
from models.base_model import BaseModel


class Post(BaseModel):
    """Creates a User Post"""

    post_id = ""
    text = ""
    user_id = ""
