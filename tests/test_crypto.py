from palobserver.crypto import generate_key, digest, sign, verify

def test_sign_roundtrip(tmp_path):
    # create a fresh keypair inside pytest's temp directory
    keyfile = tmp_path / "observer.pem"
    generate_key(keyfile.as_posix())

    blob = b"hello bundle"
    sig, pub = sign(digest(blob), keyfile)

    assert verify(digest(blob), sig, pub) is True

