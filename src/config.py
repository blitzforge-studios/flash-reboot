HOST = "127.0.0.1"
PORT = 8080

characters = []

POLICY_RESPONSE = b"""<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" to-ports="8080"/>
</cross-domain-policy>\0"""

ROGUE_ITEMS = {
    "Offhand": {
        "ID": 669,
        "Scale": 0.75,
    },
    "WholeOffhand": {
        "ID": 670,
        "Scale": 0.75,
    }
}

PALADIN_ITEMS = {
    "MainHand": {
        "ID": 1001,
        "Scale": 0.85,
    }
}