"""
Pydantic models for parsing the SRX XML
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

class JunosAddress(BaseModel):
    name: str
    ip_prefix: str = Field(alias="ip-prefix")

class JunosAddressBook(BaseModel):
    name: str
    addresses: List[JunosAddress] = Field(alias="address", default_factory=list)

# DHCP pools

class JunosDhcpAttributes(BaseModel):
    maximum_lease_time: Optional[int] = Field(None, alias="maximum-lease-time")
    domain_name: Optional[str] = Field(None, alias="domain-name")
    name_server: Optional[List[str]] = Field(default_factory=list, alias="name-server")
    router: Optional[List[str]] = Field(default_factory=list)
    propagate_settings: Optional[str] = Field(None, alias="propagate-settings")

class JunosDhcpRange(BaseModel):
    name: str
    low: str
    high: str

class JunosDhcpHost(BaseModel):
    name: str
    hardware_address: str = Field(alias="hardware-address")
    ip_address: str = Field(alias="ip-address")

class JunosDhcpFamilyInet(BaseModel):
    network: str
    range: Optional[List[JunosDhcpRange]] = Field(default_factory=list)
    dhcp_attributes: Optional[JunosDhcpAttributes] = Field(None, alias="dhcp-attributes")
    host: Optional[List[JunosDhcpHost]] = Field(default_factory=list)

class JunosDhcpPool(BaseModel):
    name: str
    family_inet: JunosDhcpFamilyInet = Field(alias="family-inet")

# security zones

def _normalise_name_list(val) -> List[str]:
    """Convert xmltodict repeated-element output to a list of name strings."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, dict):
        return [val["name"]] if "name" in val else []
    if isinstance(val, list):
        return [v["name"] if isinstance(v, dict) else v for v in val]
    return []

class JunosSystemServices(BaseModel):
    all: Optional[str] = None
    snmp: Optional[str] = None
    dhcp: Optional[str] = None
    ssh: Optional[str] = None
    ping: Optional[str] = None

class JunosProtocols(BaseModel):
    all: Optional[str] = None

class JunosHostInboundTraffic(BaseModel):
    system_services: Optional[List[str]] = Field(default_factory=list, alias="system-services")
    protocols: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def normalise_services_and_protocols(cls, data):
        if isinstance(data, dict):
            if "system-services" in data:
                data["system-services"] = _normalise_name_list(data["system-services"])
            if "protocols" in data:
                data["protocols"] = _normalise_name_list(data["protocols"])
        return data

class JunosZoneInterface(BaseModel):
    name: str
    host_inbound_traffic: Optional[JunosHostInboundTraffic] = Field(None, alias="host-inbound-traffic")

class JunosSecurityZone(BaseModel):
    name: str
    host_inbound_traffic: Optional[JunosHostInboundTraffic] = Field(None, alias="host-inbound-traffic")
    interfaces: Optional[List[JunosZoneInterface]] = Field(default_factory=list)

