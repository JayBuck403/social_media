#!/usr/bin/env python3
"""FileStorage class"""
import json
from models.base_model import BaseModel
from models.user import User
from models.post import Post
from models.comment import Comment
from models.likes import Likes


class FileStorage:
    """Creates a storage engine"""
    
    __file_path = "file.json"
    __objects = {}


    def all(self):
        """Returns the dictionary __objects"""
        return FileStorage.__objects

    def new(self, obj):
        """Sets in __objects the obj with key"""
        FileStorage.__objects["{}.{}".format(obj.__class__.__name__, obj.id)] = obj

    def save(self):
        """Serializes __objects to JSON file"""
        all_objects = FileStorage.__objects
        object_dict = {obj: all_objects[obj].to_dict() for obj in all_objects.keys()}
        with open(FileStorage.__file_path, "w") as f:
            json.dump(object_dict, f)

    def reload(self):
        """Deserializes JSON file to objects"""
        try:
            with open(FileStorage.__file_path) as f:
                object_dict = json.load(f)
                for i in object_dict.values():
                    cls_name = i["__class__"]
                    del i["__class__"]
                    self.new(eval(cls_name)(**i))
        except FileNotFoundError:
            return
