import math

class BitBuffer:
    def __init__(self):
        self.bits = []
    
    def _append_bits(self, value, bit_count):
        for i in range(bit_count - 1, -1, -1):
            bit = (value >> i) & 1
            self.bits.append(bit)
    
    def write_utf_string(self, text):
        if text is None:
            text = ""
        
        # Convert to bytes if needed
        if isinstance(text, str):
            text_bytes = text.encode('utf-8')
        else:
            text_bytes = text
            
        length = len(text_bytes)
        self._append_bits((length >> 8) & 0xff, 8)
        self._append_bits(length & 0xff, 8)
        
        for b in text_bytes:
            if isinstance(b, int):
                self._append_bits(b & 0xff, 8)
            else:
                self._append_bits(ord(b) & 0xff, 8)
    
    def write_method4(self, val):
        if val == 0:
            loc1 = 0
            loc2 = 2
            self._append_bits(loc1, 4)
            self._append_bits(val, loc2)
            return
            
        n = math.floor(math.log2(val)) + 1
        if n % 2 != 0:
            n += 1
            
        loc1 = (n >> 1) - 1
        self._append_bits(loc1, 4)
        self._append_bits(val, n)
    
    def write_method393(self, val):
        self._append_bits(val & 0xff, 8)
    
    def write_method6(self, val, bit_count):
        self._append_bits(val, bit_count)
    
    def write_method13_string(self, text):
        length = len(text)
        self.write_method4(length)
        
        for i in range(length):
            self._append_bits(ord(text[i]) & 0xff, 8)
    
    def to_bytes(self):
        # Pad to make bits a multiple of 8
        while len(self.bits) % 8 != 0:
            self.bits.append(0)
            
        result = bytearray(math.ceil(len(self.bits) / 8))
        
        for i in range(0, len(self.bits), 8):
            b = 0
            for j in range(8):
                if i + j < len(self.bits):
                    b = (b << 1) | self.bits[i + j]
            
            result[i // 8] = b
            
        return bytes(result)