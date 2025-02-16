# imports flask and databases and the classes that create the tables

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from databasev5 import db, User, CommunityLibrary, Message, Program, School, SchoolLibrary, Student, Teacher, Subscription

# class containing the CRUD operations: create, read, update and delete
class CRUDOperations:
    def __init__(self, db):
        self.db = db # initialises database

    # create funtion
    def create(self, model, **kwargs):
        try:
            instance = model(**kwargs) # new instance
            self.db.session.add(instance) # adds instance
            self.db.session.commit() # commits changes
            return instance, "Created successfully." 
        except Exception as e:
            self.db.session.rollback()
            return None, str(e) # rolls back changes if errors occur

    # read funtion
    def read(self, model, **filters):
        try:
            return model.query.filter_by(**filters).all() # gets record matching filter
        except Exception as e:
            return str(e) # errors message if exception occurs


    # update funtion
    def update(self, model, id, **updates):
        try:
            # use db.session.get to fetch the record by its primary key (id)
            record = self.db.session.get(model, id) # gets record by id
            if record:
                for key, value in updates.items():
                    setattr(record, key, value) # updates fields
                self.db.session.commit() # commits changes
                return record, "Updated successfully." 
            return None, f"{model.__name__} with id {id} not found."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e) # rolls back changes if errors occur

    # delete funtion
    def delete(self, model, id):
        try:
            # use db.session.get to fetch the record by its primary key (id)
            record = self.db.session.get(model, id) # gets record by id
            if record:
                self.db.session.delete(record) # deletes record
                self.db.session.commit() # commits changes
                return None, f"{model.__name__} with id {id} deleted successfully."
            return None, f"{model.__name__} with id {id} not found."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e) # rolls back changes if errors occur

# creayes and initialses Flask application
def create_app():
    app = Flask(__name__)
    # postgres:HashmiRF2925 should be replaced with the username and password used on each machine for now and in the future the username and password for AWS
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:HashmiRF2925@localhost/db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

crud_ops = CRUDOperations(db) #  creates instance if CRUDOperations

if __name__ == "__main__":
    app = create_app()
    with app.app_context(): # makes sure to run CRUDOperations in Flask application context
        # example data
        user_data = {
            "username": "jenny",
            "email": "ll@example.com",
            "password": "secupassword",
            "is_official": True
        }

    # example functions being used
        user, message = crud_ops.create(User, **user_data)
        print(message)

        users = crud_ops.read(User)
        print(users)


        updated_user, message = crud_ops.update(User, 1, email="mail@example.com")
        print(message)

        _, message = crud_ops.delete(User, 1)
        print(message)
