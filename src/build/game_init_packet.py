import struct

def build_game_init_packet():
    map_id, char_id = 1, 1
    start_x, start_y = 100, 200
    payload = struct.pack(">HHII", map_id, char_id, start_x, start_y)
    header = struct.pack(">HH", 0x1B, len(payload))
    return header + payload