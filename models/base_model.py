#!/usr/bin/python3
"""BaseModel class"""
import models
import uuid
from datetime import datetime


class BaseModel:
    """Creates a new BaseModel object"""

    def __init__(self, *args, **kwargs):
        """Initializes a new BaseModel object"""
        if not kwargs:
            from models import storage
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            storage.new(self)
        else:
            kwargs['updated_at'] = datetime.strptime(kwargs['updated_at'],
                                                     '%Y-%m-%dT%H:%M:%S.%f')
            kwargs['created_at'] = datetime.strptime(kwargs['created_at'],
                                                     '%Y-%m-%dT%H:%M:%S.%f')
            self.__dict__.update(kwargs)

    def save(self):
        """Updates the public instance attribute updated_at"""
        from models import storage
        self.updated_at = datetime.today()
        storage.save()

    def to_dict(self):
        """Returns a dictionary of __dict__ of the instance"""
        my_dict = self.__dict__.copy()
        my_dict["created_at"] = self.created_at.isoformat()
        my_dict["updated_at"] = self.updated_at.isoformat()
        my_dict["__class__"] = self.__class__.__name__
        return my_dict

    def __str__(self):
        """Print a string representation of the object"""
        return "[{}] ({}) {}".format(self.__class__.__name__, self.id, self.__dict__)
