"""
Pydantic models for parsing the SRX XML
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class JunosAddress(BaseModel):
    name: str
    ip_prefix: str = Field(alias="ip-prefix")

class JunosAddressBook(BaseModel):
    name: str
    addresses: List[JunosAddress] = Field(alias="address", default_factory=list)