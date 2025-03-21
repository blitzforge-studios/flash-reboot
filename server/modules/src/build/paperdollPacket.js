import { BitBuffer } from "../classes/BitBuffer.js";

function buildPaperdollPacket(character) {
    const buf = new BitBuffer();
    const [
        name,
        class_name,
        level,
        computed,
        extra1,
        extra2,
        extra3,
        extra4,
        hair_color,
        skin_color,
        shirt_color,
        pant_color,
        equipped_gear,
    ] = character;

    buf.writeUtfString(name);
    buf.writeUtfString(level);
    buf.writeUtfString(class_name);
    buf.writeUtfString(computed);
    buf.writeUtfString(extra1);
    buf.writeUtfString(extra2);
    buf.writeUtfString(extra3);
    buf.writeUtfString(extra4);
    buf.writeMethod6(hair_color, 24);
    buf.writeMethod6(skin_color, 24);
    buf.writeMethod6(shirt_color, 24);
    buf.writeMethod6(pant_color, 24);
    buf.writeUtfString(equipped_gear); // Include equipped gear in paperdoll

    const payload = buf.toBytes();
    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x7c, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildPaperdollPacket };
