"""
In-memory Database for Development
"""
from typing import Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager with in-memory storage"""
    
    _in_memory_store: dict = None
    
    @classmethod
    async def connect_db(cls, database_url: str = None, db_name: str = None):
        """Initialize in-memory storage"""
        cls._init_in_memory()
        logger.info("Using in-memory storage for development")
    
    @classmethod
    def _init_in_memory(cls):
        """Initialize in-memory storage"""
        cls._in_memory_store = {
            "users": {},
            "sessions": {},
            "messages": [],
            "vitals": []
        }
    
    @classmethod
    async def close_db(cls):
        """Close database connection"""
        logger.info("Closed database connection")
    
    @classmethod
    def get_db(cls, db_name: str = None):
        """Get database wrapper"""
        if cls._in_memory_store is None:
            cls._init_in_memory()
        return InMemoryDB(cls._in_memory_store)


class InMemoryDB:
    """In-memory database wrapper"""
    
    def __init__(self, store: dict):
        self.store = store
        self.users = InMemoryCollection(store, "users", key_field="phone")
        self.sessions = InMemoryCollection(store, "sessions", key_field="session_id")
        self.vitals_timeseries = InMemoryCollection(store, "vitals", key_field=None)


class InMemoryCollection:
    """In-memory collection that mimics MongoDB-style operations"""
    
    def __init__(self, store: dict, collection_name: str, key_field: str = None):
        self.store = store
        self.collection_name = collection_name
        self.key_field = key_field
        
        if collection_name not in self.store:
            self.store[collection_name] = {} if key_field else []
    
    async def find_one(self, query: dict, sort=None):
        """Find single document matching query"""
        data = self.store[self.collection_name]
        
        if isinstance(data, dict):
            for doc in data.values():
                if self._matches(doc, query):
                    return doc.copy()
        else:
            matches = [doc for doc in data if self._matches(doc, query)]
            if sort:
                field = sort[0][0] if isinstance(sort, list) else sort[0]
                direction = sort[0][1] if isinstance(sort, list) else sort[1]
                matches.sort(key=lambda x: x.get(field, 0), reverse=(direction == -1))
            if matches:
                return matches[0].copy()
        return None
    
    async def insert_one(self, doc: dict):
        """Insert single document"""
        data = self.store[self.collection_name]
        doc = doc.copy()
        doc["_id"] = str(uuid.uuid4())
        
        if isinstance(data, dict) and self.key_field:
            data[doc.get(self.key_field)] = doc
        elif isinstance(data, list):
            data.append(doc)
        else:
            self.store[self.collection_name] = [doc]
        
        class Result:
            inserted_id = doc["_id"]
        return Result()
    
    async def update_one(self, query: dict, update: dict):
        """Update single document"""
        data = self.store[self.collection_name]
        
        items = data.values() if isinstance(data, dict) else data
        for doc in items:
            if self._matches(doc, query):
                self._apply_update(doc, update)
                class Result:
                    modified_count = 1
                return Result()
        
        class Result:
            modified_count = 0
        return Result()
    
    def find(self, query: dict):
        """Find documents matching query"""
        return InMemoryCursor(self.store[self.collection_name], query)
    
    async def create_index(self, *args, **kwargs):
        """No-op for in-memory storage"""
        pass
    
    def _matches(self, doc: dict, query: dict) -> bool:
        """Check if document matches query"""
        return all(doc.get(k) == v for k, v in query.items())
    
    def _apply_update(self, doc: dict, update: dict):
        """Apply update operations to document"""
        if "$set" in update:
            doc.update(update["$set"])
        if "$push" in update:
            for field, value in update["$push"].items():
                if field not in doc:
                    doc[field] = []
                if isinstance(value, dict) and "$each" in value:
                    doc[field].extend(value["$each"])
                else:
                    doc[field].append(value)


class InMemoryCursor:
    """Cursor for in-memory find operations"""
    
    def __init__(self, data, query: dict):
        items = data.values() if isinstance(data, dict) else data
        self.data = [doc for doc in items if self._matches(doc, query)]
        self._sort_field = None
        self._sort_direction = 1
        self._limit = None
    
    def sort(self, field, direction=1):
        """Sort results"""
        if isinstance(field, str):
            self._sort_field = field
            self._sort_direction = direction
        elif isinstance(field, list):
            self._sort_field = field[0][0]
            self._sort_direction = field[0][1]
        return self
    
    def limit(self, n: int):
        """Limit results"""
        self._limit = n
        return self
    
    def _matches(self, doc: dict, query: dict) -> bool:
        """Check if document matches query"""
        return all(doc.get(k) == v for k, v in query.items())
    
    def __aiter__(self):
        """Async iterator"""
        data = self.data.copy()
        if self._sort_field:
            data.sort(key=lambda x: x.get(self._sort_field, 0), reverse=(self._sort_direction == -1))
        if self._limit:
            data = data[:self._limit]
        self._iter_data = iter(data)
        return self
    
    async def __anext__(self):
        """Get next item"""
        try:
            return next(self._iter_data).copy()
        except StopIteration:
            raise StopAsyncIteration


# Global database instance
db = Database()
