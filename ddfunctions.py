# imports flask and databases and the classes that create the tables

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from databasev5 import db, User, CommunityLibrary, Message, Program, School, SchoolLibrary, Student, Teacher, Subscription

# class containing the CRUD operations: create, read, update and delete

class CRUDOperations:
    def __init__(self, db):
        self.db = db # initialises database

    # create function
    def create(self, model, **kwargs):
        try:
            instance = model(**kwargs) # new instance
            self.db.session.add(instance) # adds instance
            self.db.session.commit() # commits changes
            return instance, "Created successfully."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e) # rolls back changes if errors occur

    # read function
    def read(self, model, **filters):
        try:
            return model.query.filter_by(**filters).all() # gets record matching filter
        except Exception as e:
            return str(e) # errors message if exception occurs

    # update function
    def update(self, model, id, **updates):
        try:
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

    # delete function
    def delete(self, model, id):
        try:
            record = self.db.session.get(model, id) # gets record by id
            if record:
                self.db.session.delete(record) # deletes record
                self.db.session.commit() # commits changes
                return None, f"{model.__name__} with id {id} deleted successfully."
            return None, f"{model.__name__} with id {id} not found."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e) # rolls back changes if errors occur
    
    # function to send a message
    
    def send_message(self, sender_id, receiver_id, message_content):
        try:
            message = Message(sender_id=sender_id, receiver_id=receiver_id, message_content=message_content)
            self.db.session.add(message)
            self.db.session.commit()
            return message, "Message sent successfully."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e)
    
    # function to publish content in the community library
    
    def publish_library_content(self, user_id, title):
        try:
            content = CommunityLibrary(user_id=user_id, title=title)
            self.db.session.add(content)
            self.db.session.commit()
            return content, "Content published successfully."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e)
    
    # function to get messages for a user
    
    def get_messages(self, user_id):
        try:
            messages = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).all()
            return messages, "Messages retrieved successfully."
        except Exception as e:
            return None, str(e)
    
    # function to get library content
    
    def get_library_content(self, user_id=None, title=None):
        try:
            query = CommunityLibrary.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            if title:
                query = query.filter(CommunityLibrary.title.ilike(f"%{title}%"))
            content = query.all()
            return content, "Library content retrieved successfully."
        except Exception as e:
            return None, str(e)
    
    # function to subscribe a user to a program
    
    def subscribe_to_program(self, user_id, program_id):
        try:
            subscription = Subscription(user_id=user_id, program_id=program_id)
            self.db.session.add(subscription)
            self.db.session.commit()
            return subscription, "User subscribed successfully."
        except Exception as e:
            self.db.session.rollback()
            return None, str(e)

# creates and initializes Flask application

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:HashmiRF2925@localhost/db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

crud_ops = CRUDOperations(db) # creates instance of CRUDOperations

if __name__ == "__main__":
    app = create_app()
    with app.app_context(): # makes sure to run CRUDOperations in Flask application context
        
        # example functions being used
        
        message, msg_status = crud_ops.send_message(1, 2, "Hello, how are you?")
        print(msg_status)
        
        content, content_status = crud_ops.publish_library_content(1, "New Community Post")
        print(content_status)
        
        messages, messages_status = crud_ops.get_messages(1)
        print(messages_status, messages)
        
        library_content, lib_status = crud_ops.get_library_content()
        print(lib_status, library_content)
        
        subscription, sub_status = crud_ops.subscribe_to_program(1, 1)
        print(sub_status)
