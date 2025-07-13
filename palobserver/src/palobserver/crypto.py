from pathlib import Path
from nacl.signing import SigningKey

def generate_key(path: str = "observer.pem"):
    """Create an ed25519 keypair and write <path> and <path>.pub"""
    sk = SigningKey.generate()
    Path(path).write_bytes(sk.encode())
    Path(path + ".pub").write_bytes(sk.verify_key.encode())
    return path


import hashlib
from nacl.signing import VerifyKey

def digest(data: bytes) -> bytes:
    """Return SHA-256 digest of bytes."""
    return hashlib.sha256(data).digest()

def sign(data: bytes, key_path: str = "observer.pem") -> tuple[bytes, bytes]:
    """Return (signature, public_key_bytes) for given blob."""
    sk = SigningKey(Path(key_path).read_bytes())
    sig = sk.sign(data).signature
    return sig, sk.verify_key.encode()

def verify(data: bytes, sig: bytes, pub: bytes) -> bool:
    """True if signature matches."""
    vk = VerifyKey(pub)
    try:
        vk.verify(data, sig)
        return True
    except Exception:
        return False

