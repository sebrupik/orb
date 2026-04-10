import json
import logging
from ncclient import manager
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
    with manager.connect(host=devicename, username=username, password=password, 
                         port=830, hostkey_verify=False,
                         device_params={'name':'junos'}) as m:
        # Example RPC to get address book (this is just a placeholder and may need adjustments)
        rpc = """
<get-config>
  <source>running</source>
  <filter type="subtree">
    <configuration>
      <security>
        <address-book>
          <name>default</name>
        </address-book>
      </security>
    </configuration>
  </filter>
</get-config>
"""
        response = m.dispatch(rpc)
        # Parse response into dict format expected by JunosAddressBook.model_validate
        # This parsing logic will depend on the actual structure of the response XML
        # For now, we'll return an empty dict as a placeholder
        return {}  # Replace with actual parsed data
    



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


def __main__():
    main()