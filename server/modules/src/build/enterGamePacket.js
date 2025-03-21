function buildEnterGamePacket() {
    const worldId = 1;
    const x = 100,
        y = 200,
        z = 0;
    const instanceId = 1;

    const payload = Buffer.alloc(14);
    let offset = 0;

    payload.writeUInt16BE(worldId, offset);
    offset += 2;
    payload.writeInt32BE(x, offset);
    offset += 4;
    payload.writeInt32BE(y, offset);
    offset += 4;
    payload.writeInt32BE(z, offset);
    offset += 4;
    payload.writeUInt16BE(instanceId, offset);

    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x1a, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildEnterGamePacket };
