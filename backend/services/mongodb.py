# backend/services/mongodb.py
from pymongo import MongoClient
from django.conf import settings
import datetime
from bson import ObjectId


class MongoDB:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            mongodb_config = settings.MONGODB_SETTINGS
            self._client = MongoClient(mongodb_config['host'])
            self._db = self._client[mongodb_config['db']]

    @property
    def db(self):
        return self._db

    def get_collection(self, collection_name):
        return self._db[collection_name]


# Database service instance
db = MongoDB()


class UserService:
    def __init__(self):
        self.collection = db.get_collection('users')

    def create_user(self, username, email, password):
        """Create a new user"""
        # Check if user already exists
        existing_user = self.collection.find_one({
            '$or': [
                {'username': username},
                {'email': email}
            ]
        })

        if existing_user:
            return None, "Username or email already exists"

        user_data = {
            'username': username,
            'email': email,
            'password': password,  # In production, hash this password
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
            'alphas': []
        }

        result = self.collection.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)

        # Remove password from returned data
        user_data.pop('password', None)
        return user_data, None

    def authenticate_user(self, username, password):
        """Authenticate user login"""
        user = self.collection.find_one({
            'username': username,
            'password': password  # In production, use password hashing
        })

        if user:
            user['_id'] = str(user['_id'])
            user.pop('password', None)  # Remove password from returned data
            return user, None

        return None, "Invalid username or password"

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                user.pop('password', None)
                return user, None
            return None, "User not found"
        except Exception as e:
            return None, str(e)

    def add_alpha_to_user(self, user_id, alpha_data):
        """Add an alpha strategy to a user"""
        try:
            alpha_data['id'] = str(ObjectId())  # Generate unique ID for alpha
            alpha_data['created_at'] = datetime.datetime.utcnow().isoformat()
            alpha_data['updated_at'] = datetime.datetime.utcnow().isoformat()

            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$push': {'alphas': alpha_data},
                    '$set': {'updated_at': datetime.datetime.utcnow()}
                }
            )

            if result.modified_count > 0:
                return alpha_data, None
            return None, "Failed to add alpha"
        except Exception as e:
            return None, str(e)

    def delete_alpha_from_user(self, user_id, alpha_id):
        """Delete an alpha strategy from a user"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$pull': {'alphas': {'id': alpha_id}},
                    '$set': {'updated_at': datetime.datetime.utcnow()}
                }
            )

            if result.modified_count > 0:
                return True, None
            return False, "Alpha not found or failed to delete"
        except Exception as e:
            return False, str(e)

    def update_alpha_for_user(self, user_id, alpha_id, updated_data):
        """Update an alpha strategy for a user"""
        try:
            updated_data['updated_at'] = datetime.datetime.utcnow().isoformat()

            # Update specific alpha in the alphas array
            result = self.collection.update_one(
                {'_id': ObjectId(user_id), 'alphas.id': alpha_id},
                {
                    '$set': {
                        'alphas.$': {**updated_data, 'id': alpha_id},
                        'updated_at': datetime.datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                return True, None
            return False, "Alpha not found or failed to update"
        except Exception as e:
            return False, str(e)


# Service instances
user_service = UserService()