from pymongo import MongoClient
from typing import List, Dict, Any


class MongoRepository:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_document(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        collection = self.db[collection_name]
        return collection.find_one(query)
    
    def get_documents(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        collection = self.db[collection_name]
        return list(collection.find(query))

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Any:
        collection = self.db[collection_name]
        return collection.insert_one(document).inserted_id

    def set_document(self, collection_name: str, query: Dict[str, Any], update_values: Dict[str, Any]) -> None:
        collection = self.db[collection_name]
        collection.update_one(query, {'$set': update_values})
        
    def push_document(self, collection_name: str, query: Dict[str, Any], update_values: Dict[str, Any]) -> None:
        collection = self.db[collection_name]
        collection.update_one(query, {"$push": update_values})

    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> None:
        collection = self.db[collection_name]
        collection.delete_one(query)
