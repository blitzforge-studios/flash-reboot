﻿#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket, struct, hashlib, sys, time

HOST = '127.0.0.1'
PORT = 443

# Global storage for characters.
# Each entry is a tuple:
# (name, class_name, level, computed, extra1, extra2, extra3, extra4, hair_color, skin_color, shirt_color, pant_color)
characters = []

# The Flash policy file
policy_response = b"""<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM="http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" to-ports="443"/>
</cross-domain-policy>\x00"""

def build_handshake_response(session_id):
    session_id_bytes = session_id.to_bytes(2, 'big')
    key = b"815bfb010cd7b1b4e6aa90abc7679028"
    challenge_hash = hashlib.md5(session_id_bytes + key).hexdigest()
    dummy_bytes = bytes.fromhex(challenge_hash[:12])  # first 6 bytes
    payload = session_id_bytes + dummy_bytes
    header = struct.pack(">HH", 0x12, len(payload))
    return header + payload

def build_login_challenge(challenge_str):
    cbytes = challenge_str.encode('utf-8')
    payload = struct.pack(">H", len(cbytes)) + cbytes
    header = struct.pack(">HH", 0x13, len(payload))
    return header + payload

def build_entity_packet(character, category="CharCreateUI"):
    """
    Build an entity packet from a character tuple with a configurable category.

    Parameters:
        character: Tuple containing character data.
        category: String determining the parent prefix ("CharCreateUI" or "Player").

    The character tuple format:
      (name, class_name, level, computed, extra1, extra2, extra3, extra4,
       hair_color, skin_color, shirt_color, pant_color)
    """
    (name, class_name, level, computed, extra1, extra2, extra3, extra4,
     hair_color, skin_color, shirt_color, pant_color) = character

    # Set parent based on category
    if category == "CharCreateUI":
        parent = "CharCreateUI:Starter" + class_name
    elif category == "Player":
        parent = "Player:" + class_name
    else:
        parent = category + ":" + class_name

    # Choose a scale factor (based on client defaults)
    if class_name.lower() == "paladin":
        scale = 0.85
    elif class_name.lower() == "mage":
        scale = 0.8
    elif class_name.lower() == "rogue":
        scale = 0.81
    else:
        scale = 1.0

    # Build the XML string
    xml = "<EntType EntName='PaperDoll' parent='{}'>".format(parent)
    xml += "<HairColor>{}</HairColor>".format(hair_color)
    xml += "<SkinColor>{}</SkinColor>".format(skin_color)
    xml += "<ShirtColor>{}</ShirtColor>".format(shirt_color)
    xml += "<PantColor>{}</PantColor>".format(pant_color)
    xml += "<GenderSet>{}</GenderSet>".format(computed if computed != "" else "Male")
    xml += "<HeadSet>{}</HeadSet>".format(extra1)
    xml += "<HairSet>{}</HairSet>".format(extra2)
    xml += "<MouthSet>{}</MouthSet>".format(extra3)
    xml += "<FaceSet>{}</FaceSet>".format(extra4)
    xml += "<CustomScale>{}</CustomScale>".format(scale)
    xml += "<EquippedGear></EquippedGear>"
    xml += "</EntType>"
    print("Built entity XML:", xml)
    return xml

#
# ----------------------- BIT-PACKED READING -----------------------
#

class BitReader:
    def __init__(self, data: bytes):
        self.data = data
        self.bit_index = 0

    def read_bits(self, count: int) -> int:
        result = 0
        for _ in range(count):
            byte_index = self.bit_index // 8
            bit_offset = 7 - (self.bit_index % 8)
            if byte_index >= len(self.data):
                raise ValueError("Not enough data to read")
            bit = (self.data[byte_index] >> bit_offset) & 1
            result = (result << 1) | bit
            self.bit_index += 1
        return result

    def align_to_byte(self):
        remainder = self.bit_index % 8
        if remainder != 0:
            self.bit_index += (8 - remainder)

    def read_string(self) -> str:
        self.align_to_byte()
        length = self.read_bits(16)
        result_bytes = bytearray()
        for _ in range(length):
            result_bytes.append(self.read_bits(8))
        try:
            return result_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return result_bytes.decode('latin1')

    def read_method_4(self) -> int:
        n = self.read_bits(4)
        n = (n + 1) << 1
        return self.read_bits(n)

    def read_method_393(self) -> int:
        return self.read_bits(8)

    def read_method_6(self, bit_count: int) -> int:
        return self.read_bits(bit_count)

#
# ----------------------- BIT-PACKED WRITING -----------------------
#

class BitBuffer:
    def __init__(self):
        self.bits = []

    def _append_bits(self, value, bit_count):
        for i in reversed(range(bit_count)):
            bit = (value >> i) & 1
            self.bits.append(bit)

    def write_utf_string(self, text):
        if text is None:
            text = ""
        length = len(text)
        self._append_bits((length >> 8) & 0xFF, 8)
        self._append_bits(length & 0xFF, 8)
        for ch in text:
            self._append_bits(ord(ch) & 0xFF, 8)

    def write_method_4(self, val):
        if val == 0:
            _loc1_ = 0
            _loc2_ = 2
            self._append_bits(_loc1_, 4)
            self._append_bits(val, _loc2_)
            return
        n = val.bit_length()
        if n % 2 != 0:
            n += 1
        _loc1_ = (n >> 1) - 1
        self._append_bits(_loc1_, 4)
        self._append_bits(val, n)

    def write_method_393(self, val):
        self._append_bits(val & 0xFF, 8)

    def write_method_6(self, val, bit_count):
        self._append_bits(val, bit_count)

    def write_method_13_string(self, text):
        length = len(text)
        self.write_method_4(length)
        for ch in text:
            self._append_bits(ord(ch) & 0xFF, 8)

    def to_bytes(self):
        while len(self.bits) % 8 != 0:
            self.bits.append(0)
        out = bytearray()
        for i in range(0, len(self.bits), 8):
            b = 0
            for bit in self.bits[i:i+8]:
                b = (b << 1) | bit
            out.append(b)
        return bytes(out)

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
         hair_color, skin_color, shirt_color, pant_color) = char
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
        for i in range(6):
            buf.write_method_6(0, 11)
    payload = buf.to_bytes()
    header = struct.pack(">HH", 0x15, len(payload))
    return header + payload

def build_paperdoll_packet(character):
    """Build a paperdoll packet for packet type 0x7C."""
    buf = BitBuffer()
    name, class_name, level, computed, extra1, extra2, extra3, extra4, \
    hair_color, skin_color, shirt_color, pant_color = character
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
    payload = buf.to_bytes()
    header = struct.pack(">HH", 0x7C, len(payload))
    return header + payload

def build_enter_game_packet():
    world_id = 1
    x, y, z = 100, 200, 0
    instance_id = 1
    payload = struct.pack(">HiiiH", world_id, x, y, z, instance_id)
    header = struct.pack(">HH", 0x1A, len(payload))
    return header + payload

def build_game_init_packet():
    map_id, char_id = 1, 1
    start_x, start_y = 100, 200
    payload = struct.pack(">HHII", map_id, char_id, start_x, start_y)
    header = struct.pack(">HH", 0x1B, len(payload))
    return header + payload

def handle_client(conn, addr):
    print("Connection from", addr)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            if b"<policy-file-request/>" in data:
                print("Flash policy request received. Sending policy XML.")
                conn.sendall(policy_response)
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
                except Exception as e:
                    print("Error parsing create character packet:", e)
                    continue

                print("Parsed Character Creation Packet:")
                print("  Name:     ", name)
                print("  ClassName:", class_name)
                print("  Extra:    ", [computed, extra1, extra2, extra3, extra4])
                print("  Colors:   ", [hair_color, skin_color, shirt_color, pant_color])

                new_char = (name, class_name, 1, computed, extra1, extra2, extra3, extra4,
                            hair_color, skin_color, shirt_color, pant_color)
                characters.append(new_char)
                print(f"Created new char: userID=1, name='{name}', class='{class_name}'")

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

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening on {HOST}:{PORT}...")
    while True:
        conn, addr = s.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    start_server()