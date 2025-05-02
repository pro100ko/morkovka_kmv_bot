import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from src.config import Config

# Инициализация Firebase
cred = credentials.Certificate(Config.FIREBASE_CERTIFICATE)
firebase_admin.initialize_app(cred)
db = firestore.client()

class FirebaseDB:
    @staticmethod
    def get_user(user_id):
        doc_ref = db.collection('users').document(str(user_id))
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def create_user(user_data):
        user_ref = db.collection('users').document(str(user_data['user_id']))
        user_data['registration_date'] = datetime.now()
        user_data['last_activity'] = datetime.now()
        user_ref.set(user_data)
        return user_data

    @staticmethod
    def update_user(user_id, update_data):
        user_ref = db.collection('users').document(str(user_id))
        update_data['last_activity'] = datetime.now()
        user_ref.update(update_data)

    @staticmethod
    def get_categories():
        categories_ref = db.collection('categories').order_by('order')
        return [doc.to_dict() for doc in categories_ref.stream()]

    @staticmethod
    def get_category(category_id):
        category_ref = db.collection('categories').document(str(category_id))
        doc = category_ref.get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_products_by_category(category_id):
        products_ref = db.collection('products').where('category_id', '==', category_id)
        return [doc.to_dict() for doc in products_ref.stream()]

    @staticmethod
    def get_product(product_id):
        product_ref = db.collection('products').document(str(product_id))
        doc = product_ref.get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def search_products(query):
        products_ref = db.collection('products')
        query_ref = products_ref.where('name', '>=', query).where('name', '<=', query + '\uf8ff').limit(Config.MAX_SEARCH_RESULTS)
        return [doc.to_dict() for doc in query_ref.stream()]

    @staticmethod
    def create_product(product_data):
        product_ref = db.collection('products').document()
        product_data['id'] = product_ref.id
        product_data['created_at'] = datetime.now()
        product_data['updated_at'] = datetime.now()
        product_ref.set(product_data)
        return product_data

    @staticmethod
    def update_product(product_id, update_data):
        product_ref = db.collection('products').document(str(product_id))
        update_data['updated_at'] = datetime.now()
        product_ref.update(update_data)

    @staticmethod
    def get_tests():
        tests_ref = db.collection('tests')
        return [doc.to_dict() for doc in tests_ref.stream()]

    @staticmethod
    def get_test(test_id):
        test_ref = db.collection('tests').document(str(test_id))
        doc = test_ref.get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def create_test(test_data):
        test_ref = db.collection('tests').document()
        test_data['id'] = test_ref.id
        test_data['created_at'] = datetime.now()
        test_ref.set(test_data)
        return test_data

    @staticmethod
    def save_test_result(result_data):
        result_ref = db.collection('test_results').document()
        result_data['completion_date'] = datetime.now()
        result_ref.set(result_data)
        return result_data

    @staticmethod
    def get_user_test_results(user_id):
        results_ref = db.collection('test_results').where('user_id', '==', str(user_id))
        return [doc.to_dict() for doc in results_ref.stream()]