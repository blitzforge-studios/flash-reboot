from ..classes.bit_buffer import BitBuffer
import struct

def build_paperdoll_packet(character):
    """Build a paperdoll packet for packet type 0x7C."""
    buf = BitBuffer()
    name, class_name, level, computed, extra1, extra2, extra3, extra4, \
    hair_color, skin_color, shirt_color, pant_color, equipped_gear = character
    buf.write_utf_string(name)
    buf.write_utf_string(class_name)
    buf.write_utf_string(computed)
    buf.write_utf_string(extra1)
    buf.write_utf_string(extra2)
    buf.write_utf_string(extra3)
    buf.write_utf_string(extra4)
    buf.write_method_6(hair_color, 24)
    buf.write_method_6(skin_color, 24)
    buf.write_method_6(shirt_color, 24)
    buf.write_method_6(pant_color, 24)
    buf.write_utf_string(equipped_gear)  # Include equipped gear in paperdoll
    payload = buf.to_bytes()
    header = struct.pack(">HH", 0x7C, len(payload))
    return header + payload