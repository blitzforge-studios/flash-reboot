def build_game_init_packet():
    map_id = 1
    char_id = 1
    start_x = 100
    start_y = 200
    
    # Create payload buffer
    payload = bytearray(12)
    offset = 0
    
    # Write data to payload
    payload[offset:offset+2] = map_id.to_bytes(2, byteorder='big')
    offset += 2
    
    payload[offset:offset+2] = char_id.to_bytes(2, byteorder='big')
    offset += 2
    
    payload[offset:offset+4] = start_x.to_bytes(4, byteorder='big')
    offset += 4
    
    payload[offset:offset+4] = start_y.to_bytes(4, byteorder='big')
    
    # Create header
    header = bytearray(4)
    header[0:2] = (0x1b).to_bytes(2, byteorder='big')
    header[2:4] = len(payload).to_bytes(2, byteorder='big')
    
    return bytes(header + payload)