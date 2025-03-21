class BitReader {
    constructor(data) {
        this.data = data;
        this.bitIndex = 0;
    }

    readBits(count) {
        let result = 0;
        for (let i = 0; i < count; i++) {
            const byteIndex = Math.floor(this.bitIndex / 8);
            const bitOffset = 7 - (this.bitIndex % 8);
            if (byteIndex >= this.data.length) {
                throw new Error("Not enough data to read");
            }
            const bit = (this.data[byteIndex] >> bitOffset) & 1;
            result = (result << 1) | bit;
            this.bitIndex += 1;
        }
        return result;
    }

    alignToByte() {
        const remainder = this.bitIndex % 8;
        if (remainder !== 0) {
            this.bitIndex += 8 - remainder;
        }
    }

    readString() {
        this.alignToByte();
        const length = this.readBits(16);
        const resultBytes = Buffer.alloc(length);
        for (let i = 0; i < length; i++) {
            resultBytes[i] = this.readBits(8);
        }
        try {
            return resultBytes.toString("utf-8");
        } catch (e) {
            return resultBytes.toString("latin1");
        }
    }

    readMethod4() {
        const n = this.readBits(4);
        const bitCount = (n + 1) << 1;
        return this.readBits(bitCount);
    }

    readMethod393() {
        return this.readBits(8);
    }

    readMethod6(bitCount) {
        return this.readBits(bitCount);
    }
}

export { BitReader };
