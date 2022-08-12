from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class NodeTimeRange(BaseModel):
    create_st: datetime = None
    create_et: datetime = None

class NodeBase(BaseModel):
    nodeName: str
    flag: int=0
    nodeHost: Optional[str]=None
    nodePort: Optional[str] = None

class NodeCreate(NodeBase):
    brif: str=None
    appKey: str=None

class NodeQuery(BaseModel):
    code: str=None
    nodeName: str=None
    brif: str=None
    time_range: NodeTimeRange = None
    flag: Optional[int]=None

class NodeUpdate(NodeBase):
    nodeName: Optional[str]=None
    flag: Optional[int]=None
    brif: str=None
    nodeHost: Optional[str]=None
    nodePort: Optional[str] = None

class NodeReturn(NodeBase):
    brif: str=None
    expire_time: datetime=None
    appKey: str=None
    class Config:
        orm_mode=True
