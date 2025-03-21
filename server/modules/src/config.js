const HOST = "127.0.0.1";
const PORT = 443;

let characters = [];

const POLICY_RESPONSE = Buffer.from(
    `<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" to-ports="443"/>
</cross-domain-policy>\0`,
    "utf8"
);

const ROGUE_ITEMS = {
    Offhand: {
        ID: 669,
        Scale: 0.75,
    },
    WholeOffhand: {
        ID: 670,
        Scale: 0.75,
    },
};

const PALADIN_ITEMS = {
    MainHand: {
        ID: 1001,
        Scale: 0.85,
    },
};

export { HOST, PORT, characters, POLICY_RESPONSE, ROGUE_ITEMS, PALADIN_ITEMS };
