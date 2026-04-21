import json
import xmltodict

import models.junos
from ncclient import manager
from ncclient.xml_ import to_ele

class JunosConnector:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

    def connect(self):
        # Placeholder for connection logic using ncclient
        with manager.connect(host=self.host, username=self.username, password=self.password, 
                         port=22, hostkey_verify=False,
                         device_params={'name':'junos'}) as m:
            print(m.server_capabilities)  # For debugging purposes
            self.collect_configuration(m)


    def collect_configuration(self, m):
        # Placeholder for logic to collect data from Junos
        self.configuration = {
            "security_zones": self.get_security_zones(m),
            "interfaces": self.get_interfaces(m),
        }
        print(self.configuration)  # For debugging purposes

    def normalise_zone_interfaces(interfaces_raw) -> list:
        """Normalise xmltodict interface output to a list of dicts."""
        if interfaces_raw is None:
            return []
        # Single interface with no children may be a plain string
        if isinstance(interfaces_raw, str):
            return [{"name": interfaces_raw}]
        # Single interface with children is a dict
        if isinstance(interfaces_raw, dict):
            interfaces_raw = [interfaces_raw]
        result = []
        for iface in interfaces_raw:
            if isinstance(iface, str):
                result.append({"name": iface})
            else:
                result.append(iface)
        return result


    def get_security_zones(self, m):
        # Placeholder for logic to retrieve security zones from Junos
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
        parsed = xmltodict.parse(response.data_xml)
        print(json.dumps(parsed, indent=2))  # See the real structure
        # return parsed
        try:
            all_zones = parsed["rpc-reply"]["data"]["configuration"]["security"]["zones"]["security-zone"]
        except KeyError as e:
            # logger.error(f"Missing key in NETCONF response: {e}")
            all_zones = None

        # Validate Junos input
        # normalise interfaces in each zone first
        for zone in all_zones:
            if "interfaces" in zone:
                # zone["interfaces"]["interface"] = self.normalise_zone_interfaces(zone["interfaces"]["interface"])
                if isinstance(zone["interfaces"], dict):
                    zone["interfaces"] = [{"name": zone["interfaces"]["name"]}]

        junos_zones = [models.junos.JunosSecurityZone.model_validate(raw_junos_dict) for raw_junos_dict in all_zones]

        return junos_zones

    def get_interfaces(self, m):
        # Placeholder for logic to retrieve interfaces from Junos
        pass

    def get_address_books(self, m):
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
        # print(json.dumps(parsed, indent=2))  # See the real structure

        # Then, access keys carefully:
        try:
            all_address_books = parsed["rpc-reply"]["data"]["configuration"]["security"]
        except KeyError as e:
            # logger.error(f"Missing key in NETCONF response: {e}")
            all_address_books = None

        # Validate Junos input
        junos_book = models.junos.JunosAddressBook.model_validate(raw_junos_dict)

        return junos_book