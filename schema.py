from pydantic import BaseModel
from typing import List, Dict, Any

class Inventory(BaseModel):
    stock: int
    sku: str

class Product(BaseModel):
    name: str
    slug: str
    category: str
    subCategory: str
    brand: str
    price: float
    currency: str
    inventory: Inventory
    attributes: Dict[str, Any]
    tags: List[str]
    rating: float
    isActive: bool

class CacheMeta(BaseModel):
    cache_source: str
    cache_status: str
    backend_time_ms: float
    total_time_ms: float
