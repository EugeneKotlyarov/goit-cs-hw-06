# from cred import *
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# MONGO PART
DB_URI = f"mongodb://admin111:admin111@localhost/?retryWrites=true&w=majority"
DB_NAME = "msg_db"
COLL_NAME = "messages"
client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db[COLL_NAME]

# Отримання всіх записів
documents = collection.find()

# Виведення результатів
for doc in documents:
    print(doc)
