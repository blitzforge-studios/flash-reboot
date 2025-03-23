import time
import struct
from ..config import POLICY_RESPONSE, characters, ROGUE_ITEMS, PALADIN_ITEMS
from ..classes.bit_reader import BitReader
from ..classes.bit_buffer import BitBuffer
from ..build.export_builds import (
    build_handshake_response,
    build_enter_game_packet,
    build_game_init_packet,
    build_login_character_list_bitpacked,
    build_login_challenge,
    build_paperdoll_packet
)
from ..build.entity_packet import build_entity_packet

def handle_client(conn, addr):
    print("Connection from", addr)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            if b"<policy-file-request/>" in data:
                print("Flash policy request received. Sending policy XML.")
                conn.sendall(POLICY_RESPONSE)
                continue

            hex_data = data.hex()
            print("Received raw data:", hex_data)

            if len(hex_data) < 4:
                continue

            try:
                pkt_type = int(hex_data[:4], 16)
            except ValueError:
                print("Error parsing packet type.")
                continue

            if pkt_type == 0x11:
                session_id = int(hex_data[8:12], 16) if len(hex_data) >= 12 else 0
                print(f"Got handshake packet (0x11), session ID = {session_id}")
                resp = build_handshake_response(session_id)
                conn.sendall(resp)
                print("Sent handshake response (0x12):", resp.hex())
                time.sleep(0.2)
                challenge_packet = build_login_challenge("CHALLENGE")
                conn.sendall(challenge_packet)
                print("Sent login challenge (0x13):", challenge_packet.hex())
                time.sleep(0.2)

            elif pkt_type in (0x13, 0x14):
                print("Got authentication packet (0x13/0x14). Parsing...")
                pkt = build_login_character_list_bitpacked()
                conn.sendall(pkt)
                print("Sent login character list (0x15):", pkt.hex())
                time.sleep(0.2)

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

                    # Sınıfa göre varsayılan donanımı ayarla
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
                    else:  # Mage ve diğer sınıflar için
                        default_gear = "<Item Slot='1' ID='1001' Name='StarterSword' Scale='1.0'/>"

                    # Yeni karakter oluştur
                    new_char = (
                        name, class_name, 1, computed, extra1, extra2, extra3, extra4,
                        hair_color, skin_color, shirt_color, pant_color, default_gear
                    )
                    
                    # Debug bilgisi
                    print("Parsed Character Creation Packet:")
                    print("  Name:     ", name)
                    print("  ClassName:", class_name)
                    print("  Extra:    ", [computed, extra1, extra2, extra3, extra4])
                    print("  Colors:   ", [hair_color, skin_color, shirt_color, pant_color])
                    print("  Gear:     ", default_gear)

                    # Karakteri bir kez ekle
                    characters.append(new_char)
                    print(f"Created new char: userID=1, name='{name}', class='{class_name}'")

                except Exception as e:
                    print("Error parsing create character packet:", e)
                    continue

                pkt = build_login_character_list_bitpacked()
                conn.sendall(pkt)
                print("Sent updated login character list (0x15):", pkt.hex())
                time.sleep(0.2)

                ack_pkt = struct.pack(">HH", 0x16, 0)
                conn.sendall(ack_pkt)
                print("Sent character select acknowledgment (0x16):", ack_pkt.hex())
                time.sleep(0.2)

                enter_packet = build_enter_game_packet()
                conn.sendall(enter_packet)
                print("Sent enter game packet (0x1A):", enter_packet.hex())
                time.sleep(0.2)

                init_pkt = build_game_init_packet()
                conn.sendall(init_pkt)
                print("Sent game init packet (0x1B):", init_pkt.hex())
                time.sleep(0.2)

                paperdoll_xml = build_entity_packet(new_char, category="CharCreateUI")
                buf = BitBuffer()
                buf.write_utf_string(paperdoll_xml)
                pd_payload = buf.to_bytes()
                pd_pkt = struct.pack(">HH", 0x7C, len(pd_payload)) + pd_payload
                conn.sendall(pd_pkt)
                print("Sent paperdoll update (0x7C):", pd_pkt.hex())
                time.sleep(0.2)

            elif pkt_type == 0x16:
                print("Got character select packet (0x16).")
                
                # Önce karakter bilgilerini gönder
                for char in characters:
                    br = BitReader(data[4:])  # Skip the header
                    selected_name = br.read_string()
                    if char[0] == selected_name:
                        paperdoll_xml = build_entity_packet(char, category="Player")
                        buf = BitBuffer()
                        buf.write_utf_string(paperdoll_xml)
                        pd_payload = buf.to_bytes()
                        pd_pkt = struct.pack(">HH", 0x7C, len(pd_payload)) + pd_payload
                        conn.sendall(pd_pkt)
                        print("Sent paperdoll update (0x7C)")
                        time.sleep(0.1)
                        break
                
                # Sonra diğer paketleri gönder
                ack_pkt = struct.pack(">HH", 0x16, 0)
                conn.sendall(ack_pkt)
                time.sleep(0.1)
                
                enter_packet = build_enter_game_packet()
                conn.sendall(enter_packet)
                time.sleep(0.1)
                
                init_pkt = build_game_init_packet()
                conn.sendall(init_pkt)
                time.sleep(0.1)

            elif pkt_type == 0x19:
                print("Got packet type 0x19. Request for character details.")
                payload = data[4:]  # Skip 4-byte header (type + length)
                br = BitReader(payload)
                try:
                    name = br.read_string()
                    print(f"Requested character: {name}")
                    # Find character by name
                    for char in characters:
                        if char[0] == name:
                            xml = build_entity_packet(char, category="Player")
                            buf = BitBuffer()
                            buf.write_utf_string(xml)
                            pd_payload = buf.to_bytes()
                            pd_pkt = struct.pack(">HH", 0x7C, len(pd_payload)) + pd_payload
                            conn.sendall(pd_pkt)
                            print("Sent paperdoll update (0x7C):", pd_pkt.hex())
                            break
                    else:
                        print(f"Character '{name}' not found.")
                        ack_pkt = struct.pack(">HH", 0x19, 0)
                        conn.sendall(ack_pkt)
                        print("Sent 0x19 ack:", ack_pkt.hex())
                except Exception as e:
                    print("Error parsing 0x19 packet:", e)
                    ack_pkt = struct.pack(">HH", 0x19, 0)
                    conn.sendall(ack_pkt)
                    print("Sent 0x19 ack:", ack_pkt.hex())
                time.sleep(0.2)

            elif pkt_type == 0x7C:
                print("Received packet type 0x7C. (Appearance/cue update)")
                if characters:
                    entity_xml = build_entity_packet(characters[0], category="Player")
                    buf = BitBuffer()
                    buf.write_utf_string(entity_xml)
                    payload = buf.to_bytes()
                    response = struct.pack(">HH", 0x7C, len(payload)) + payload
                    conn.sendall(response)
                    print("Sent entity packet (0x7C):", response.hex())
                else:
                    print("No character data available. Sending empty 0x7C response.")
                    response = struct.pack(">HH", 0x7C, 0)
                    conn.sendall(response)
                    print("Sent 0x7C response:", response.hex())
                time.sleep(0.2)

    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()
        print("Client disconnected.")
