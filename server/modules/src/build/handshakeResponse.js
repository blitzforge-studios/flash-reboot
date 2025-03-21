import { createHash } from "crypto";

function buildHandshakeResponse(sessionId) {
    const sessionIdBuffer = Buffer.alloc(2);

    sessionIdBuffer.writeUInt16BE(sessionId, 0);

    const key = Buffer.from("815bfb010cd7b1b4e6aa90abc7679028", "hex");
    const hash = createHash("md5")
        .update(Buffer.concat([sessionIdBuffer, key]))
        .digest("hex");
    const dummyBytes = Buffer.from(hash.substring(0, 12), "hex");
    const payload = Buffer.concat([sessionIdBuffer, dummyBytes]);
    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x12, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildHandshakeResponse };
