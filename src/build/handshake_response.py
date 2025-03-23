import hashlib

def build_handshake_response(session_id):
    # Create buffer for session ID
    session_id_buffer = bytearray(2)
    session_id_buffer[0:2] = session_id.to_bytes(2, byteorder='big')
    
    # Create key and hash
    key = bytes.fromhex("815bfb010cd7b1b4e6aa90abc7679028")
    hash_input = session_id_buffer + key
    hash_result = hashlib.md5(hash_input).hexdigest()
    
    # Get first 12 chars of hash as bytes
    dummy_bytes = bytes.fromhex(hash_result[:12])
    
    # Create payload
    payload = session_id_buffer + dummy_bytes
    
    # Create header
    header = bytearray(4)
    header[0:2] = (0x12).to_bytes(2, byteorder='big')
    header[2:4] = len(payload).to_bytes(2, byteorder='big')
    
    return bytes(header + payload)