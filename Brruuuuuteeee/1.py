import string
import re

ct  = bytes.fromhex("4c554645445455045f68674d424f684d5e415e52494346495270747b784a")
key = b"/,4*7"

# ── Repeating-key XOR decrypt ─────────────────────────────────────────────────
pt = bytes(ct[i] ^ key[i % len(key)] for i in range(len(ct)))

print("=" * 55)
print("  Cipher  : Repeating-Key XOR (Vigenère-XOR)")
print(f"  Key      : {key}  ({len(key)} bytes)")
print(f"  CT len   : {len(ct)} bytes  →  key repeats {len(ct) // len(key)}×")
print("=" * 55)

# ── Key derivation proof (first 6 bytes vs known prefix) ─────────────────────
print("\nKey derivation from known prefix 'cyros{':\n")
known_prefix = b"cyros{"
for i, (c, p) in enumerate(zip(ct, known_prefix)):
    derived = c ^ p
    print(f"  offset {i}: 0x{c:02x} ^ 0x{p:02x} ('{chr(p)}') "
          f"= 0x{derived:02x} ('{chr(derived)}')")

# ── Regex validation ──────────────────────────────────────────────────────────
print("\nFlag validation:")
try:
    flag = pt.decode("ascii")
    if re.fullmatch(r'cyros\{[!-~]+\}', flag):
        print(f"  ✓ Valid flag format")
        print(f"  ✓ Score  : {sum(10 if c in string.ascii_letters else 8 if c in string.digits + '_{} ' else 2 for c in flag)}")
    print(f"  ✓ Flag   : {flag}")
except UnicodeDecodeError:
    print("  ✗ Decryption produced non-ASCII output — wrong key")

# ── Key stream visualisation ──────────────────────────────────────────────────
print("\nKey stream across 30 bytes:\n")
key_stream = "".join(chr(key[i % len(key)]) for i in range(len(ct)))
print(f"  Key stream : {key_stream}")
print(f"  Ciphertext : {ct.hex()}")
print(f"  Plaintext  : {flag}")