import { Buffer } from "node:buffer";

import { characters } from "../config.js";
import { BitBuffer } from "../classes/BitBuffer.js";

function buildLoginCharacterListBitpacked() {
    const buf = new BitBuffer();
    const userId = 1;
    const maxChars = 8;
    const charCount = characters.length;

    buf.writeMethod4(userId);
    buf.writeMethod393(maxChars);
    buf.writeMethod393(charCount);

    for (const char of characters) {
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
        ] = char;

        buf.writeUtfString(name);
        buf.writeUtfString(class_name);
        buf.writeMethod6(level, 6);
        buf.writeMethod6(hair_color, 24);
        buf.writeMethod6(pant_color, 24);
        buf.writeMethod6(shirt_color, 24);
        buf.writeMethod6(skin_color, 24);
        buf.writeUtfString(extra4);
        buf.writeUtfString(computed);
        buf.writeUtfString(extra2);
        buf.writeUtfString(extra1);
        buf.writeUtfString(extra3);
        buf.writeUtfString(equipped_gear);

        for (let i = 0; i < 6; i++) {
            buf.writeMethod6(0, 11);
        }
    }

    const payload = buf.toBytes();
    const header = Buffer.alloc(4);

    header.writeUInt16BE(0x15, 0);
    header.writeUInt16BE(payload.length, 2);

    return Buffer.concat([header, payload]);
}

export { buildLoginCharacterListBitpacked };
