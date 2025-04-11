from ..config import characters
from ..classes.bit_buffer import BitBuffer
import struct

def build_login_character_list_bitpacked():
    buf = BitBuffer()
    user_id = 1
    max_chars = 8
    char_count = len(characters)

    buf.write_method_4(user_id)
    buf.write_method_393(max_chars)
    buf.write_method_393(char_count)

    for char in characters:
        (name, class_name, level, computed, extra1, extra2, extra3, extra4,
         hair_color, skin_color, shirt_color, pant_color, equipped_gear) = char
        buf.write_utf_string(name)
        buf.write_utf_string(class_name)
        buf.write_method_6(level, 6)
        buf.write_method_6(hair_color, 24)
        buf.write_method_6(pant_color, 24)
        buf.write_method_6(shirt_color, 24)
        buf.write_method_6(skin_color, 24)
        buf.write_utf_string(extra4)
        buf.write_utf_string(computed)
        buf.write_utf_string(extra2)
        buf.write_utf_string(extra1)
        buf.write_utf_string(extra3)
        buf.write_utf_string(equipped_gear)  # Write equipped gear
        for i in range(6):
            buf.write_method_6(0, 11)
    payload = buf.to_bytes()
    header = struct.pack(">HH", 0x15, len(payload))
    return header + payload