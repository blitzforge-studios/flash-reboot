function buildGameInitPacket() {
    const mapId = 1,
        charId = 1;
    const startX = 100,
        startY = 200;

    const payload = Buffer.alloc(12);
    let offset = 0;

    payload.writeUInt16BE(mapId, offset);
    offset += 2;
    payload.writeUInt16BE(charId, offset);
    offset += 2;
    payload.writeUInt32BE(startX, offset);
    offset += 4;
    payload.writeUInt32BE(startY, offset);

    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x1b, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildGameInitPacket };
