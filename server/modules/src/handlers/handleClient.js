import { Buffer } from "node:buffer";
import { Socket } from "node:net";

import { POLICY_RESPONSE, characters } from "../config.js";
import {
    buildEnterGamePacket,
    buildGameInitPacket,
    buildHandshakeResponse,
    buildLoginChallenge,
    buildLoginCharacterListBitpacked,
} from "../build/exportBuilds.js";
import { BitReader } from "../classes/BitReader.js";
import { BitBuffer } from "../classes/BitBuffer.js";
import { buildEntityPacket } from "../build/entityPacket.js";

// Paket gönderme işlemini bir fonksiyona çıkaralım
function sendPacketSequence(socket, char) {
    return new Promise((resolve) => {
        // 1. Önce character acknowledgment
        const ackPkt = Buffer.alloc(4);
        ackPkt.writeUInt16BE(0x16, 0);
        ackPkt.writeUInt16BE(0, 2);
        socket.write(ackPkt);
        console.log("Sent character select acknowledgment (0x16)");

        // 2. Enter game packet
        setTimeout(() => {
            const enterPacket = buildEnterGamePacket();
            socket.write(enterPacket);
            console.log("Sent enter game packet (0x1A)");

            // 3. Game init packet
            setTimeout(() => {
                const initPkt = buildGameInitPacket();
                socket.write(initPkt);
                console.log("Sent game init packet (0x1B)");

                // 4. Entity/Paperdoll packet
                setTimeout(() => {
                    const entityXml = buildEntityPacket(char, "Player");
                    const buf = new BitBuffer();
                    buf.writeUtfString(entityXml);
                    const payload = buf.toBytes();

                    const pdPktHeader = Buffer.alloc(4);
                    pdPktHeader.writeUInt16BE(0x7c, 0);
                    pdPktHeader.writeUInt16BE(payload.length, 2);

                    const finalPacket = Buffer.concat([pdPktHeader, payload]);
                    socket.write(finalPacket);
                    console.log("Sent entity packet (0x7C)");

                    resolve();
                }, 300);
            }, 300);
        }, 300);
    });
}

function handleClient(socket = new Socket()) {
    console.log("Connection from", socket.remoteAddress);

    socket.on("error", (err) => {
        console.error("Socket error:", err);
    });

    socket.on("data", (data) => {
        if (data.includes(Buffer.from("<policy-file-request/>"))) {
            console.log("Flash policy request received. Sending policy XML.");
            socket.write(POLICY_RESPONSE);
            return;
        }

        const hexData = data.toString("hex");
        console.log("Received raw data:", hexData);

        if (hexData.length < 4) {
            return;
        }

        try {
            const pktType = parseInt(hexData.substring(0, 4), 16);

            if (pktType === 0x11) {
                const sessionId =
                    hexData.length >= 12
                        ? parseInt(hexData.substring(8, 12), 16)
                        : 0;
                console.log(
                    `Got handshake packet (0x11), session ID = ${sessionId}`
                );
                const resp = buildHandshakeResponse(sessionId);
                socket.write(resp);
                console.log(
                    "Sent handshake response (0x12):",
                    resp.toString("hex")
                );
                setTimeout(() => {
                    const challengePacket = buildLoginChallenge("CHALLENGE");
                    socket.write(challengePacket);
                    console.log(
                        "Sent login challenge (0x13):",
                        challengePacket.toString("hex")
                    );
                }, 200);
            } else if (pktType === 0x13 || pktType === 0x14) {
                console.log(
                    "Got authentication packet (0x13/0x14). Parsing..."
                );
                const pkt = buildLoginCharacterListBitpacked();
                socket.write(pkt);
                console.log(
                    "Sent login character list (0x15):",
                    pkt.toString("hex")
                );
            } else if (pktType === 0x17) {
                console.log(
                    "Got character creation packet (0x17). Parsing creation data..."
                );
                const payload = data.subarray(4);
                try {
                    const br = new BitReader(payload);
                    const name = br.readString();
                    const class_name = br.readString();
                    const computed = br.readString();
                    const extra1 = br.readString();
                    const extra2 = br.readString();
                    const extra3 = br.readString();
                    const extra4 = br.readString();
                    const hair_color = br.readBits(24);
                    const skin_color = br.readBits(24);
                    const shirt_color = br.readBits(24);
                    const pant_color = br.readBits(24);

                    // Set default gear based on class
                    let default_gear;
                    if (class_name.toLowerCase() === "mage") {
                        default_gear = `
                            <Item Slot='MainHand' ID='1002' Scale='1.0'/>
                            <Item Slot='OffHand' ID='1003' Scale='0.8'/>
                        `;
                    } else if (class_name.toLowerCase() === "rogue") {
                        default_gear = `
                            <Item Slot='Offhand' ID='${ROGUE_ITEMS["Offhand"]["ID"]}' Scale='${ROGUE_ITEMS["Offhand"]["Scale"]}'/>
                            <Item Slot='WholeOffhand' ID='${ROGUE_ITEMS["WholeOffhand"]["ID"]}' Scale='${ROGUE_ITEMS["WholeOffhand"]["Scale"]}'/>
                        `;
                    } else if (class_name.toLowerCase() === "paladin") {
                        default_gear = `
                            <Item Slot='MainHand' ID='${PALADIN_ITEMS["MainHand"]["ID"]}' Scale='${PALADIN_ITEMS["MainHand"]["Scale"]}'/>
                        `;
                    } else {
                        // Mage and other classes
                        default_gear =
                            "<Item Slot='1' ID='1001' Name='StarterSword' Scale='1.0'/>";
                    }

                    // Create new character
                    const new_char = [
                        name,
                        class_name,
                        1,
                        computed,
                        extra1,
                        extra2,
                        extra3,
                        extra4,
                        hair_color,
                        skin_color,
                        shirt_color,
                        pant_color,
                        default_gear,
                    ];

                    // Debug info
                    console.log("Parsed Character Creation Packet:");
                    console.log("  Name:     ", name);
                    console.log("  ClassName:", class_name);
                    console.log("  Extra:    ", [
                        computed,
                        extra1,
                        extra2,
                        extra3,
                        extra4,
                    ]);
                    console.log("  Colors:   ", [
                        hair_color,
                        skin_color,
                        shirt_color,
                        pant_color,
                    ]);
                    console.log("  Gear:     ", default_gear);

                    // Add character once
                    characters.push(new_char);
                    console.log(
                        `Created new char: userID=1, name='${name}', class='${class_name}'`
                    );

                    const pkt = buildLoginCharacterListBitpacked();
                    socket.write(pkt);
                    console.log(
                        "Sent updated login character list (0x15):",
                        pkt.toString("hex")
                    );

                    setTimeout(() => {
                        const ackPkt = Buffer.alloc(4);
                        ackPkt.writeUInt16BE(0x16, 0);
                        ackPkt.writeUInt16BE(0, 2);
                        socket.write(ackPkt);
                        console.log(
                            "Sent character select acknowledgment (0x16):",
                            ackPkt.toString("hex")
                        );

                        setTimeout(() => {
                            const enterPacket = buildEnterGamePacket();
                            socket.write(enterPacket);
                            console.log(
                                "Sent enter game packet (0x1A):",
                                enterPacket.toString("hex")
                            );

                            setTimeout(() => {
                                const initPkt = buildGameInitPacket();
                                socket.write(initPkt);
                                console.log(
                                    "Sent game init packet (0x1B):",
                                    initPkt.toString("hex")
                                );

                                setTimeout(() => {
                                    const paperdollXml = buildEntityPacket(
                                        new_char,
                                        "CharCreateUI"
                                    );
                                    const buf = new BitBuffer();
                                    buf.writeUtfString(paperdollXml);
                                    const pdPayload = buf.toBytes();
                                    const pdPktHeader = Buffer.alloc(4);
                                    pdPktHeader.writeUInt16BE(0x7c, 0);
                                    pdPktHeader.writeUInt16BE(
                                        pdPayload.length,
                                        2
                                    );
                                    const pdPkt = Buffer.concat([
                                        pdPktHeader,
                                        pdPayload,
                                    ]);
                                    socket.write(pdPkt);
                                    console.log(
                                        "Sent paperdoll update (0x7C):",
                                        pdPkt.toString("hex")
                                    );
                                }, 200);
                            }, 200);
                        }, 200);
                    }, 200);
                } catch (e) {
                    console.log("Error parsing create character packet:", e);
                }
            } else if (pktType === 0x16) {
                console.log("Got character select packet (0x16)");

                const br = new BitReader(data.subarray(4));
                const selectedName = br.readString();

                // Karakteri bul
                const selectedChar = characters.find(
                    (char) => char[0] === selectedName
                );

                if (selectedChar) {
                    try {
                        sendPacketSequence(socket, selectedChar).catch(
                            (err) => {
                                console.error(
                                    "Error sending packet sequence:",
                                    err
                                );
                            }
                        );
                    } catch (err) {
                        console.error("Error sending packet sequence:", err);
                    }
                } else {
                    console.log(`Character '${selectedName}' not found`);
                }
            } else if (pktType === 0x19) {
                console.log(
                    "Got packet type 0x19. Request for character details."
                );
                const payload = data.subarray(4); // Skip 4-byte header (type + length)
                try {
                    const br = new BitReader(payload);
                    const name = br.readString();
                    console.log(`Requested character: ${name}`);

                    // Find character by name
                    let found = false;
                    for (const char of characters) {
                        if (char[0] === name) {
                            const xml = buildEntityPacket(char, "Player");
                            const buf = new BitBuffer();
                            buf.writeUtfString(xml);
                            const pdPayload = buf.toBytes();
                            const pdPktHeader = Buffer.alloc(4);
                            pdPktHeader.writeUInt16BE(0x7c, 0);
                            pdPktHeader.writeUInt16BE(pdPayload.length, 2);
                            const pdPkt = Buffer.concat([
                                pdPktHeader,
                                pdPayload,
                            ]);
                            socket.write(pdPkt);
                            console.log(
                                "Sent paperdoll update (0x7C):",
                                pdPkt.toString("hex")
                            );
                            found = true;
                            break;
                        }
                    }

                    if (!found) {
                        console.log(`Character '${name}' not found.`);
                        const ackPkt = Buffer.alloc(4);
                        ackPkt.writeUInt16BE(0x19, 0);
                        ackPkt.writeUInt16BE(0, 2);
                        socket.write(ackPkt);
                        console.log("Sent 0x19 ack:", ackPkt.toString("hex"));
                    }
                } catch (e) {
                    console.log("Error parsing 0x19 packet:", e);
                    const ackPkt = Buffer.alloc(4);
                    ackPkt.writeUInt16BE(0x19, 0);
                    ackPkt.writeUInt16BE(0, 2);
                    socket.write(ackPkt);
                    console.log("Sent 0x19 ack:", ackPkt.toString("hex"));
                }
            } else if (pktType === 0x7c) {
                console.log(
                    "Received packet type 0x7C. (Appearance/cue update)"
                );
                if (characters.length > 0) {
                    const entityXml = buildEntityPacket(
                        characters[0],
                        "Player"
                    );
                    const buf = new BitBuffer();
                    buf.writeUtfString(entityXml);
                    const payload = buf.toBytes();
                    const responseHeader = Buffer.alloc(4);
                    responseHeader.writeUInt16BE(0x7c, 0);
                    responseHeader.writeUInt16BE(payload.length, 2);
                    const response = Buffer.concat([responseHeader, payload]);
                    socket.write(response);
                    console.log(
                        "Sent entity packet (0x7C):",
                        response.toString("hex")
                    );
                } else {
                    console.log(
                        "No character data available. Sending empty 0x7C response."
                    );
                    const response = Buffer.alloc(4);
                    response.writeUInt16BE(0x7c, 0);
                    response.writeUInt16BE(0, 2);
                    socket.write(response);
                    console.log(
                        "Sent 0x7C response:",
                        response.toString("hex")
                    );
                }
            }
        } catch (e) {
            console.log("Error processing packet:", e);
        }
    });

    socket.on("close", () => {
        console.log("Client disconnected.");
    });
}

export { handleClient };
