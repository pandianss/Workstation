from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class MasterRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    code: str
    name_en: str
    name_hi: Optional[str] = None
    name_local: Optional[str] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
