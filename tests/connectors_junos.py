import pytest
from unittest.mock import MagicMock, patch
import xmltodict

from connectors.junos import JunosConnector
from models.junos import JunosAddressBook, JunosAddress, JunosSecurityZone, JunosVlans, JunosVlan
from tests.junos_rpc import (show_configuration_security_address_book,
                             show_configuration_securiy_zones,
                             show_configuration_vlans)


def make_mock_manager(xml_response: str):
    """Helper to create a mock ncclient manager whose dispatch returns the given XML."""
    mock_response = MagicMock()
    mock_response.data_xml = xml_response
    mock_m = MagicMock()
    mock_m.dispatch.return_value = mock_response
    return mock_m


class TestConnectorsJunos:

    @pytest.fixture
    def connector(self):
        return JunosConnector("192.168.1.250", "cs7_admin", "testpass")

    def test_connector_instantiation(self, connector):
        assert connector is not None
        assert connector.get_security_zones is not None
        assert connector.get_interfaces is not None
        assert connector.get_address_books is not None

    @pytest.mark.parametrize("xml_input, expected_name, expected_addresses", [
        (
            show_configuration_security_address_book,
            "global",
            [
                ("server002.cs7networks.co.uk",   "10.83.20.11/32"),
                ("WIRELESS-01_subnet",            "192.168.1.0/24"),
                ("server002.cs7networks.co.uk-v6","2001:270:6aaa:20::11/128"),
                ("firmware.grandstream.com",       None),
            ],
        ),
    ])
    def test_get_address_books(self, connector, xml_input, expected_name, expected_addresses):
        mock_m = make_mock_manager(xml_input)

        result = connector.get_address_books(mock_m)

        assert isinstance(result, JunosAddressBook)
        assert result.name == expected_name
        assert len(result.addresses) == len(expected_addresses)

        for addr, (exp_name, exp_prefix) in zip(result.addresses, expected_addresses):
            assert isinstance(addr, JunosAddress)
            assert addr.name == exp_name
            assert addr.ip_prefix == exp_prefix

    @pytest.mark.parametrize("xml_input, expected_zones", [
        (
            show_configuration_securiy_zones,
            [
                {
                    "name": "OUTSIDE",
                    "system_services": ["ping", "ntp", "bootp", "dhcp", "dhcpv6"],
                    "interfaces": ["pt-1/0/0.0", "pp0.0"],
                },
                {
                    "name": "MGMT",
                    "system_services": ["all"],
                    "interfaces": ["irb.2"],
                },
                {
                    "name": "WIRELESS_01",
                    "system_services": ["all"],
                    "interfaces": ["irb.30", "irb.3"],
                },
            ],
        ),
    ])
    def test_get_security_zones(self, connector, xml_input, expected_zones):
        mock_m = make_mock_manager(xml_input)
        result = connector.get_security_zones(mock_m)

        assert isinstance(result, list)
        assert len(result) == len(expected_zones)

        for zone, expected in zip(result, expected_zones):
            assert isinstance(zone, JunosSecurityZone)
            assert zone.name == expected["name"]
            assert zone.host_inbound_traffic.system_services == expected["system_services"]
            iface_names = [iface.name for iface in zone.interfaces]
            assert iface_names == expected["interfaces"]

    @pytest.mark.parametrize("xml_input, expected_vlans", [
        (
            show_configuration_vlans,
            [
                {"name": "IOT_01",              "vlan_id": 31, "l3_interface": "irb.31"},
                {"name": "MGMT",                "vlan_id": 2,  "l3_interface": "irb.2"},
                {"name": "PROXMOX_NO_INTERNET", "vlan_id": 15, "l3_interface": "irb.15"},
            ],
        ),
    ])
    def test_get_vlans(self, connector, xml_input, expected_vlans):
        mock_m = make_mock_manager(xml_input)
        result = connector.get_vlans(mock_m)

        assert isinstance(result, JunosVlans)
        assert len(result.vlans) == len(expected_vlans)

        for vlan, expected in zip(result.vlans, expected_vlans):
            assert isinstance(vlan, JunosVlan)
            assert vlan.name == expected["name"]
            assert vlan.vlan_id == expected["vlan_id"]
            assert vlan.l3_interface == expected["l3_interface"]
