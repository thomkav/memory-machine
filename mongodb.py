import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


password = os.getenv("MONGODB_PASSWORD")
if not password:
    raise ValueError("MONGODB_PASSWORD environment variable not set")

uri = f"mongodb+srv://memorymachineingest:{password}@memorymachine.njy48tk.mongodb.net/?retryWrites=true&w=majority&appName=memorymachine"  # noqa:E501

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
