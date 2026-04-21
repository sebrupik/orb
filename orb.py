"""
OPNsense Rule Bridge
"""

import json
import logging
import xmltodict
from ncclient import manager
from ncclient.xml_ import to_ele
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.junos import JunosAddressBook
from models.opnsense import OPNsenseAlias

logger = logging.getLogger(__name__)


def junos_collector(devicename: str, username: str, password: str) -> Dict[str, Any]:
    """
    Collect address book data from a Junos device using netconf.

    : param devicename: Hostname or IP of the Junos device.
    : param username: Username for authentication.
    : param password: Password for authentication.

    : return: Raw data dict suitable for JunosAddressBook.model_validate.
    """
    # Placeholder for actual netconf collection logic
    # In a real implementation, this would use ncclient or similar to connect to the device,
    # execute the appropriate RPC to retrieve the address book, and parse it into a dict.
    # raise NotImplementedError("Junos collector not implemented yet")

    print("pre manager.connect")  # For debugging purposes

    with manager.connect(host=devicename, username=username, password=password, 
                         port=22, hostkey_verify=False,
                         device_params={'name':'junos'}) as m:
        print(m.server_capabilities)  # For debugging purposes

        interfaces = junos_get_interfaces(m)
        print("Collected interfaces:", interfaces)

        # Example RPC to get address book (this is just a placeholder and may need adjustments)
        zones = junos_get_security_zones(m)
        print("Collected zones:", zones)

        address_book = junos_get_address_books(m, zone_name="example-zone")  # Replace with actual zone name
        print("Collected address book:", address_book)
    
    
def junos_get_interfaces(m: manager.Manager) -> Dict[str, Any]:
    # Placeholder for function to get interfaces from Junos
    rpc = """<get-config>
    <source><running/></source>
    <filter type="subtree">
        <configuration>
            <interfaces/>
        </configuration>
    </filter>
</get-config>"""
    
    response = m.dispatch(to_ele(rpc))
    # Parse response into dict format expected by JunosAddressBook.model_validate
    # This parsing logic will depend on the actual structure of the response XML
    # For now, we'll return an empty dict as a placeholder
    parsed = xmltodict.parse(response.data_xml)
    print(json.dumps(parsed, indent=2))  # See the real structure

    # raise NotImplementedError("Junos interfaces collector not implemented yet")


def junos_get_security_zones(m: manager.Manager) -> Dict[str, Any]:
    # Placeholder for function to get security zones from Junos
    rpc = """<get-config>
    <source><running/></source>
    <filter type="subtree">
        <configuration>
            <security>
                <zones/>
            </security>
        </configuration>
    </filter>
</get-config>"""
    
    response = m.dispatch(to_ele(rpc))
    # Parse response into dict format expected by JunosAddressBook.model_validate
    # This parsing logic will depend on the actual structure of the response XML
    # For now, we'll return an empty dict as a placeholder
    parsed = xmltodict.parse(response.data_xml)
    print(json.dumps(parsed, indent=2))  # See the real structure

    # raise NotImplementedError("Junos security zones collector not implemented yet")


def junos_get_address_books(m: manager.Manager, zone_name: str) -> Dict[str, Any]:
    # itterate through security zones and collect address books for each zone
    #  take the zone name and use that and use in the subtree filter to collect
    rpc = """
<get-config>
  <source><running/></source>
  <filter type="subtree">
    <configuration>
      <security>
        <address-book/>
      </security>
    </configuration>
  </filter>
</get-config>
"""
    response = m.dispatch(to_ele(rpc))
    # Parse response into dict format expected by JunosAddressBook.model_validate
    # This parsing logic will depend on the actual structure of the response XML
    # For now, we'll return an empty dict as a placeholder
    parsed = xmltodict.parse(response.data_xml)
    print(json.dumps(parsed, indent=2))  # See the real structure

    # Then, access keys carefully:
    try:
        all_address_books = parsed["rpc-reply"]["data"]["configuration"]["security"]
    except KeyError as e:
        logger.error(f"Missing key in NETCONF response: {e}")
        all_address_books = None

    return all_address_books




def translate_aliases(raw_junos_dict: Dict[str, Any],
                      template_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Translate a Junos address book dict into a list of OPNSense alias payload dicts.

    : param raw_junos_dict: Raw data that JunosAddressBook.model_validate accepts.
    : param template_path: Optional path to JSON template (defaults to templates/alias.json).

    : return: List of payload dicts ready to POST to OPNSense.
    """
    if template_path is None:
        template_path = Path(__file__).parent / "templates" / "alias.json"

    # Validate Junos input
    junos_book = JunosAddressBook.model_validate(raw_junos_dict)

    # Read template
    try:
        template_str = Path(template_path).read_text(encoding="utf-8")
    except Exception as e:
        logger.error("Failed to read template %s: %s", template_path, e)
        raise

    # Prefer Jinja2 if available for safer templating
    use_jinja = False
    try:
        from jinja2 import Template  # type: ignore
        use_jinja = True
    except Exception:
        logger.debug("Jinja2 not available, falling back to simple replace")

    opnsense_payloads: List[Dict[str, Any]] = []

    for addr in junos_book.addresses:
        os_alias = OPNsenseAlias(name=addr.name, content=addr.ip_prefix)

        try:
            if use_jinja:
                final_str = Template(template_str).render(name=os_alias.name,
                                                          ip_address=os_alias.content)
            else:
                # safe replace of known tokens
                final_str = template_str.replace("{{ name }}", os_alias.name) \
                                        .replace("{{ ip_address }}", os_alias.content)
            payload = json.loads(final_str)
        except json.JSONDecodeError as je:
            logger.error("Template produced invalid JSON for %s: %s", os_alias.name, je)
            raise
        except Exception as e:
            logger.error("Error rendering template for %s: %s", os_alias.name, e)
            raise

        opnsense_payloads.append(payload)

    return opnsense_payloads


def main():
    # collect parameters, eg: soruce vendor (ie Juniper, Cisco, etc)

    # depending on source vendor, collect data (eg: via API, etc)
    # if Juniper use netconf to collect data
    pass


def __main__():
    main()
