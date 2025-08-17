#!/usr/bin/env python3
# LSB image steganography with optional XOR keystream "encryption"
# Format: [magic 4B][flags 1B][payload_len 4B][nonce 8B][payload...]
# flags bit0 = XOR on/off

from PIL import Image
import sys, os, struct, hashlib

MAGIC = b'ISTJ'  # marker so we only decode our own payloads

def keystream(password: str, nonce: bytes):
    # Infinite XOR keystream via SHA256(password || nonce || counter)
    counter = 0
    seed = password.encode('utf-8') + nonce
    while True:
        h = hashlib.sha256(seed + counter.to_bytes(8,'big')).digest()
        for b in h:
            yield b
        counter += 1

def xor_bytes(data: bytes, password: str, nonce: bytes) -> bytes:
    if not password:
        return data
    ks = keystream(password, nonce)
    return bytes(b ^ next(ks) for b in data)

def _bits(bytes_like):
    for byte in bytes_like:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

def _bytes_from_bits(bit_iter, nbytes):
    out = bytearray()
    byte = 0
    for i in range(nbytes * 8):
        bit = next(bit_iter)
        byte = (byte << 1) | bit
        if (i + 1) % 8 == 0:
            out.append(byte)
            byte = 0
    return bytes(out)

def hide(cover_path, out_path, payload_bytes, password=""):
    im = Image.open(cover_path).convert("RGBA")
    pixels = bytearray(im.tobytes())  # RGBA stream
    capacity_bits = len(pixels)       # 1 bit per channel byte

    # Build header
    use_xor = 1 if password else 0
    import os
    nonce = os.urandom(8)
    enc_payload = xor_bytes(payload_bytes, password, nonce) if password else payload_bytes
    header = MAGIC + struct.pack("B", use_xor) + struct.pack(">I", len(enc_payload)) + nonce
    bitstream = list(_bits(header + enc_payload))

    if len(bitstream) > capacity_bits:
        raise ValueError(f"Payload too large. Need {len(bitstream)} bits, have {capacity_bits}.")

    # Embed
    for i, bit in enumerate(bitstream):
        pixels[i] = (pixels[i] & 0xFE) | bit

    stego = Image.frombytes("RGBA", im.size, bytes(pixels))
    stego.save(out_path)
    im.close()

def reveal(stego_path, password=""):
    im = Image.open(stego_path).convert("RGBA")
    pixels = im.tobytes()
    bit_iter = ((b & 1) for b in pixels)

    # Read header: 4 + 1 + 4 + 8 = 17 bytes
    header = _bytes_from_bits(bit_iter, 17)
    if header[:4] != MAGIC:
        raise ValueError("No payload found (bad magic).")
    use_xor = header[4]
    (length,) = struct.unpack(">I", header[5:9])
    nonce = header[9:17]

    # Read payload
    payload = _bytes_from_bits(bit_iter, length)
    if use_xor:
        payload = xor_bytes(payload, password, nonce)
    im.close()
    return payload

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Hide text:    python imgstego.py hide cover.png out.png \"secret text\" [password]")
        print("  Hide file:    python imgstego.py hidefile cover.png out.png input.bin [password]")
        print("  Reveal:       python imgstego.py reveal stego.png [password] > output")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "hide":
        _, _, cover, outp, text, *rest = sys.argv
        pwd = rest[0] if rest else ""
        hide(cover, outp, text.encode('utf-8'), pwd)
    elif mode == "hidefile":
        _, _, cover, outp, infile, *rest = sys.argv
        pwd = rest[0] if rest else ""
        data = open(infile, "rb").read()
        hide(cover, outp, data, pwd)
    elif mode == "reveal":
        _, _, stego, *rest = sys.argv
        pwd = rest[0] if rest else ""
        sys.stdout.buffer.write(reveal(stego, pwd))
    else:
        print("Unknown mode.")

if __name__ == "__main__":
    main()
