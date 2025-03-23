from ..config import characters
from ..classes.bit_buffer import BitBuffer

def build_login_character_list_bitpacked():
    buffer = BitBuffer()
    buffer.write_method4(11)  # Packet ID
    buffer.write_method393(0)  # Status code
    
    # Write character count
    buffer.write_method4(len(characters))
    
    # Write each character's data
    for char in characters:
        buffer.write_method13_string(char[0])  # Name
        buffer.write_method6(char[2], 32)      # Level
        
    return buffer.to_bytes()