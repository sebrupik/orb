import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OpnSenseConnector:
    def __init__(self, api_key, api_secret, base_url, verify_ssl=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.verify_ssl = verify_ssl

    def connect(self):
        with requests.Session() as session:
            session.auth = (self.api_key, self.api_secret)
            # session.headers.update({'Content-Type': 'application/json'})
            session.verify = self.verify_ssl
            response = session.get(f"{self.base_url}/api/core/firmware/status")
            print(response.status_code, response.text)  # Debugging output
            if response.status_code == 200:
                print("Successfully connected to OPNsense API")
                self.collect_configuration(session)
            else:
                print(f"Failed to connect to OPNsense API: {response.status_code} - {response.text}")

    def collect_configuration(self, session):
        # Placeholder for method to collect configuration data from OPNsense
        self.configuration = {
            "firewall_rules": self.get_firewall_rules(),
            "interfaces": self.get_interfaces(),
        }
        print({k: len(v) if v is not None else None for k, v in self.configuration.items()})  # Show counts

    def get_firewall_rules(self):
        # Placeholder for method to retrieve firewall rules from OPNsense
        pass

    def add_firewall_rule(self, rule):
        # Placeholder for method to add a firewall rule to OPNsense
        pass

    def delete_firewall_rule(self, rule_id):
        # Placeholder for method to delete a firewall rule from OPNsense
        pass

    def get_interfaces(self):
        # Placeholder for method to retrieve interfaces from OPNsense
        pass