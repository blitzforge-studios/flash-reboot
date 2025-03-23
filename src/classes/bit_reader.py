class BitReader:
    def __init__(self, data):
        self.data = data
        self.bit_index = 0
    
    def read_bits(self, count):
        result = 0
        for i in range(count):
            byte_index = self.bit_index // 8
            bit_offset = 7 - (self.bit_index % 8)
            
            if byte_index >= len(self.data):
                raise Exception("Not enough data to read")
                
            bit = (self.data[byte_index] >> bit_offset) & 1
            result = (result << 1) | bit
            self.bit_index += 1
            
        return result
    
    def align_to_byte(self):
        remainder = self.bit_index % 8
        if remainder != 0:
            self.bit_index += 8 - remainder
    
    def read_string(self):
        self.align_to_byte()
        length = self.read_bits(16)
        
        result_bytes = bytearray(length)
        for i in range(length):
            result_bytes[i] = self.read_bits(8)
            
        try:
            return result_bytes.decode('utf-8')
        except Exception:
            return result_bytes.decode('latin1')
    
    def read_method4(self):
        n = self.read_bits(4)
        bit_count = (n + 1) << 1
        return self.read_bits(bit_count)
    
    def read_method393(self):
        return self.read_bits(8)
    
    def read_method6(self, bit_count):
        return self.read_bits(bit_count)