import { Buffer } from "node:buffer";

export function buildEnterGamePacket() {
    // Eğer özel bir payload varsa, onu oluşturun. Örnekte boş payload kullanılıyor.
    const payload = Buffer.alloc(0);
    // Header (4 bayt) + payload uzunluğu kadar buffer ayırın.
    const buf = Buffer.alloc(4 + payload.length);
    // Packet tipini (ör: 0x1A) header'a yazın.
    buf.writeUInt16BE(0x1a, 0);
    // Payload uzunluğunu header'ın devamına yazın.
    buf.writeUInt16BE(payload.length, 2);
    // Eğer payload varsa, buffer'a kopyalayın.
    // payload.copy(buf, 4);
    return buf;
}
