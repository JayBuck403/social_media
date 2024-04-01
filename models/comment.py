#!/usr/bin/env python3
"""Comment Class"""
from models.base_model import BaseModel


class Comment(BaseModel):
    """Creates a User Comment"""

    comment_id = ""
    user_id = ""
    comment = ""
    post_id = ""
