function buildLoginChallenge(challengeStr) {
    const cbytes = Buffer.from(challengeStr, "utf-8");
    const lengthBuffer = Buffer.alloc(2);

    lengthBuffer.writeUInt16BE(cbytes.length, 0);

    const payload = Buffer.concat([lengthBuffer, cbytes]);
    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x13, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildLoginChallenge };
