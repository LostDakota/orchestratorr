
from pydantic import BaseModel
from typing import Optional

class DiskSpace(BaseModel):
    id: Optional[int] = None
    path: str
    label: str
    freeSpace: int
    totalSpace: int
    
class ClientUsedSpace(BaseModel):
    clientName: str
    path: str
    freeSpace: int
    totalSpace: int
    usedSpace: int