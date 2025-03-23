def build_enter_game_packet():
    # If there's a special payload, create it. Using empty payload in the example.
    payload = bytes()
    
    # Create buffer for header (4 bytes) + payload length
    buf = bytearray(4 + len(payload))
    
    # Write packet type (e.g. 0x1A) to header
    buf[0:2] = (0x1a).to_bytes(2, byteorder='big')
    
    # Write payload length to the rest of the header
    buf[2:4] = len(payload).to_bytes(2, byteorder='big')
    
    # If there's payload, copy it to the buffer
    # payload_bytes = bytearray(payload)
    # buf[4:4+len(payload)] = payload_bytes
    
    return bytes(buf)