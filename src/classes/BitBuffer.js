class BitBuffer {
    constructor() {
        this.bits = [];
    }

    _appendBits(value, bitCount) {
        for (let i = bitCount - 1; i >= 0; i--) {
            const bit = (value >> i) & 1;
            this.bits.push(bit);
        }
    }

    writeUtfString(text) {
        if (text === null || text === undefined) {
            text = "";
        }
        const length = Buffer.byteLength(text, "utf8");
        this._appendBits((length >> 8) & 0xff, 8);
        this._appendBits(length & 0xff, 8);
        for (let i = 0; i < text.length; i++) {
            this._appendBits(text.charCodeAt(i) & 0xff, 8);
        }
    }

    writeMethod4(val) {
        if (val === 0) {
            const loc1 = 0;
            const loc2 = 2;
            this._appendBits(loc1, 4);
            this._appendBits(val, loc2);
            return;
        }
        let n = Math.floor(Math.log2(val)) + 1;
        if (n % 2 !== 0) {
            n += 1;
        }
        const loc1 = (n >> 1) - 1;
        this._appendBits(loc1, 4);
        this._appendBits(val, n);
    }

    writeMethod393(val) {
        this._appendBits(val & 0xff, 8);
    }

    writeMethod6(val, bitCount) {
        this._appendBits(val, bitCount);
    }

    writeMethod13String(text) {
        const length = text.length;
        this.writeMethod4(length);
        for (let i = 0; i < text.length; i++) {
            this._appendBits(text.charCodeAt(i) & 0xff, 8);
        }
    }

    toBytes() {
        while (this.bits.length % 8 !== 0) {
            this.bits.push(0);
        }
        const out = Buffer.alloc(Math.ceil(this.bits.length / 8));
        for (let i = 0; i < this.bits.length; i += 8) {
            let b = 0;
            for (let j = 0; j < 8 && i + j < this.bits.length; j++) {
                b = (b << 1) | this.bits[i + j];
            }
            out[i / 8] = b;
        }
        return out;
    }
}

export { BitBuffer };
