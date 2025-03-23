import time
from config import POLICY_RESPONSE, characters, ROGUE_ITEMS, PALADIN_ITEMS
from ..classes.bit_reader import BitReader
from ..classes.bit_buffer import BitBuffer
from ..build.export_builds import (
    build_enter_game_packet,
    build_game_init_packet,
    build_handshake_response,
    build_login_challenge,
    build_login_character_list_bitpacked
)
from ..build.entity_packet import build_entity_packet

def send_packet_sequence(socket, char):
    # 1. Send character acknowledgment
    ack_pkt = bytearray(4)
    ack_pkt[0:2] = (0x16).to_bytes(2, byteorder='big')
    ack_pkt[2:4] = (0).to_bytes(2, byteorder='big')
    socket.send(ack_pkt)
    print("Sent character select acknowledgment (0x16)")
    
    # 2. Enter game packet
    time.sleep(0.3)
    enter_packet = build_enter_game_packet()
    socket.send(enter_packet)
    print("Sent enter game packet (0x1A)")
    
    # 3. Game init packet
    time.sleep(0.3)
    init_pkt = build_game_init_packet()
    socket.send(init_pkt)
    print("Sent game init packet (0x1B)")
    
    # 4. Entity/Paperdoll packet
    time.sleep(0.3)
    entity_xml = build_entity_packet(char, "Player")
    buf = BitBuffer()
    buf.write_utf_string(entity_xml)
    payload = buf.to_bytes()
    
    pd_pkt_header = bytearray(4)
    pd_pkt_header[0:2] = (0x7c).to_bytes(2, byteorder='big')
    pd_pkt_header[2:4] = len(payload).to_bytes(2, byteorder='big')
    
    final_packet = pd_pkt_header + payload
    socket.send(final_packet)
    print("Sent entity packet (0x7C)")

def handle_client(socket):
    print(f"Connection from {socket.getpeername()}")
    
    try:
        while True:
            data = socket.recv(4096)
            if not data:
                break
                
            # Check for Flash policy request
            if b"<policy-file-request/>" in data:
                print("Flash policy request received. Sending policy XML.")
                socket.send(POLICY_RESPONSE)
                continue
                
            hex_data = data.hex()
            print(f"Received raw data: {hex_data}")
            
            if len(hex_data) < 4:
                continue
                
            pkt_type = int(hex_data[0:4], 16)
            
            if pkt_type == 0x11:
                session_id = int(hex_data[8:12], 16) if len(hex_data) >= 12 else 0
                print(f"Got handshake packet (0x11), session ID = {session_id}")
                
                resp = build_handshake_response(session_id)
                socket.send(resp)
                print(f"Sent handshake response (0x12): {resp.hex()}")
                
                time.sleep(0.2)
                challenge_packet = build_login_challenge("CHALLENGE")
                socket.send(challenge_packet)
                print(f"Sent login challenge (0x13): {challenge_packet.hex()}")
                
            elif pkt_type in (0x13, 0x14):
                print("Got authentication packet (0x13/0x14). Parsing...")
                
                pkt = build_login_character_list_bitpacked()
                socket.send(pkt)
                print(f"Sent login character list (0x15): {pkt.hex()}")
                
            elif pkt_type == 0x17:
                print("Got character creation packet (0x17). Parsing creation data...")
                
                payload = data[4:]
                try:
                    br = BitReader(payload)
                    name = br.read_string()
                    class_name = br.read_string()
                    computed = br.read_string()
                    extra1 = br.read_string()
                    extra2 = br.read_string()
                    extra3 = br.read_string()
                    extra4 = br.read_string()
                    hair_color = br.read_bits(24)
                    skin_color = br.read_bits(24)
                    shirt_color = br.read_bits(24)
                    pant_color = br.read_bits(24)
                    
                    # Set default gear based on class
                    if class_name.lower() == "mage":
                        default_gear = """
                            <Item Slot='MainHand' ID='1002' Scale='1.0'/>
                            <Item Slot='OffHand' ID='1003' Scale='0.8'/>
                        """
                    elif class_name.lower() == "rogue":
                        default_gear = f"""
                            <Item Slot='Offhand' ID='{ROGUE_ITEMS["Offhand"]["ID"]}' Scale='{ROGUE_ITEMS["Offhand"]["Scale"]}'/>
                            <Item Slot='WholeOffhand' ID='{ROGUE_ITEMS["WholeOffhand"]["ID"]}' Scale='{ROGUE_ITEMS["WholeOffhand"]["Scale"]}'/>
                        """
                    elif class_name.lower() == "paladin":
                        default_gear = f"""
                            <Item Slot='MainHand' ID='{PALADIN_ITEMS["MainHand"]["ID"]}' Scale='{PALADIN_ITEMS["MainHand"]["Scale"]}'/>
                        """
                    else:
                        # Mage and other classes
                        default_gear = "<Item Slot='1' ID='1001' Name='StarterSword' Scale='1.0'/>"
                    
                    # Create new character
                    new_char = [
                        name,
                        class_name,
                        1,  # level
                        computed,
                        extra1,
                        extra2,
                        extra3,
                        extra4,
                        hair_color,
                        skin_color,
                        shirt_color,
                        pant_color,
                        default_gear,
                    ]
                    
                    # Debug info
                    print("Parsed Character Creation Packet:")
                    print(f"  Name:     {name}")
                    print(f"  ClassName:{class_name}")
                    print(f"  Extra:    {[computed, extra1, extra2, extra3, extra4]}")
                    print(f"  Colors:   {[hair_color, skin_color, shirt_color, pant_color]}")
                    print(f"  Gear:     {default_gear}")
                    
                    # Add character
                    characters.append(new_char)
                    print(f"Created new char: userID=1, name='{name}', class='{class_name}'")
                    
                    pkt = build_login_character_list_bitpacked()
                    socket.send(pkt)
                    print(f"Sent updated login character list (0x15): {pkt.hex()}")
                    
                    time.sleep(0.2)
                    ack_pkt = bytearray(4)
                    ack_pkt[0:2] = (0x16).to_bytes(2, byteorder='big')
                    ack_pkt[2:4] = (0).to_bytes(2, byteorder='big')
                    socket.send(ack_pkt)
                    print(f"Sent character select acknowledgment (0x16): {ack_pkt.hex()}")
                    
                    time.sleep(0.2)
                    enter_packet = build_enter_game_packet()
                    socket.send(enter_packet)
                    print(f"Sent enter game packet (0x1A): {enter_packet.hex()}")
                    
                    time.sleep(0.2)
                    init_pkt = build_game_init_packet()
                    socket.send(init_pkt)
                    print(f"Sent game init packet (0x1B): {init_pkt.hex()}")
                    
                    time.sleep(0.2)
                    paperdoll_xml = build_entity_packet(new_char, "CharCreateUI")
                    buf = BitBuffer()
                    buf.write_utf_string(paperdoll_xml)
                    pd_payload = buf.to_bytes()
                    
                    pd_pkt_header = bytearray(4)
                    pd_pkt_header[0:2] = (0x7c).to_bytes(2, byteorder='big')
                    pd_pkt_header[2:4] = len(pd_payload).to_bytes(2, byteorder='big')
                    
                    pd_pkt = pd_pkt_header + pd_payload
                    socket.send(pd_pkt)
                    print(f"Sent paperdoll update (0x7C): {pd_pkt.hex()}")
                    
                except Exception as e:
                    print(f"Error parsing create character packet: {e}")
                    
            elif pkt_type == 0x16:
                print("Got character select packet (0x16)")
                
                br = BitReader(data[4:])
                selected_name = br.read_string()
                
                # Find character
                selected_char = None
                for char in characters:
                    if char[0] == selected_name:
                        selected_char = char
                        break
                
                if selected_char:
                    try:
                        send_packet_sequence(socket, selected_char)
                    except Exception as err:
                        print(f"Error sending packet sequence: {err}")
                else:
                    print(f"Character '{selected_name}' not found")
                    
            elif pkt_type == 0x19:
                print("Got packet type 0x19. Request for character details.")
                
                payload = data[4:]  # Skip 4-byte header (type + length)
                try:
                    br = BitReader(payload)
                    name = br.read_string()
                    print(f"Requested character: {name}")
                    
                    # Find character by name
                    found = False
                    for char in characters:
                        if char[0] == name:
                            xml = build_entity_packet(char, "Player")
                            buf = BitBuffer()
                            buf.write_utf_string(xml)
                            pd_payload = buf.to_bytes()
                            
                            pd_pkt_header = bytearray(4)
                            pd_pkt_header[0:2] = (0x7c).to_bytes(2, byteorder='big')
                            pd_pkt_header[2:4] = len(pd_payload).to_bytes(2, byteorder='big')
                            
                            pd_pkt = pd_pkt_header + pd_payload
                            socket.send(pd_pkt)
                            print(f"Sent paperdoll update (0x7C): {pd_pkt.hex()}")
                            found = True
                            break
                            
                    if not found:
                        print(f"Character '{name}' not found.")
                        ack_pkt = bytearray(4)
                        ack_pkt[0:2] = (0x19).to_bytes(2, byteorder='big')
                        ack_pkt[2:4] = (0).to_bytes(2, byteorder='big')
                        socket.send(ack_pkt)
                        print(f"Sent 0x19 ack: {ack_pkt.hex()}")
                except Exception as e:
                    print(f"Error parsing 0x19 packet: {e}")
                    ack_pkt = bytearray(4)
                    ack_pkt[0:2] = (0x19).to_bytes(2, byteorder='big')
                    ack_pkt[2:4] = (0).to_bytes(2, byteorder='big')
                    socket.send(ack_pkt)
                    print(f"Sent 0x19 ack: {ack_pkt.hex()}")
                    
            elif pkt_type == 0x7c:
                print("Received packet type 0x7C. (Appearance/cue update)")
                
                if characters:
                    entity_xml = build_entity_packet(characters[0], "Player")
                    buf = BitBuffer()
                    buf.write_utf_string(entity_xml)
                    payload = buf.to_bytes()
                    
                    response_header = bytearray(4)
                    response_header[0:2] = (0x7c).to_bytes(2, byteorder='big')
                    response_header[2:4] = len(payload).to_bytes(2, byteorder='big')
                    
                    response = response_header + payload
                    socket.send(response)
                    print(f"Sent entity packet (0x7C): {response.hex()}")
                else:
                    print("No character data available. Sending empty 0x7C response.")
                    response = bytearray(4)
                    response[0:2] = (0x7c).to_bytes(2, byteorder='big')
                    response[2:4] = (0).to_bytes(2, byteorder='big')
                    socket.send(response)
                    print(f"Sent 0x7C response: {response.hex()}")
                    
    except Exception as e:
        print(f"Error processing packet: {e}")
    finally:
        print("Client disconnected.")
        socket.close()