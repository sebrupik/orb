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
