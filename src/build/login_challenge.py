def build_login_challenge(challenge_str):
    # Convert challenge string to bytes
    cbytes = challenge_str.encode('utf-8')
    
    # Create length buffer
    length_buffer = bytearray(2)
    length_buffer[0:2] = len(cbytes).to_bytes(2, byteorder='big')
    
    # Create payload
    payload = length_buffer + cbytes
    
    # Create header
    header = bytearray(4)
    header[0:2] = (0x13).to_bytes(2, byteorder='big')
    header[2:4] = len(payload).to_bytes(2, byteorder='big')
    
    return bytes(header + payload)