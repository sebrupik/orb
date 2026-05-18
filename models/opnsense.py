"""
Pydantic models for parsing the OPNSense JSON
"""
from pydantic import BaseModel, Field, model_validator

class OPNsenseAlias(BaseModel):
    name: str
    content: str
    description: str = "Imported from SRX"

    @model_validator(mode="before")
    def clean_name(cls, v):
        # OPNsense API rejects names with dots or spaces
        return v.replace(".", "_").replace(" ", "_")