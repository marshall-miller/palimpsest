from types import SimpleNamespace
from palobserver.bundle import build_bundle
from palobserver.crypto import generate_key, verify, digest
import json

def test_build_bundle_signature(tmp_path):
    # generate a temp key inside pytest's tmp dir
    keyfile = tmp_path / "observer.pem"
    generate_key(keyfile.as_posix())

    doc = SimpleNamespace(page_content="Net-30 terms.", metadata={})
    hdr, body = build_bundle([doc], key_path=keyfile.as_posix())

    # header checks
    assert "bundle_id" in hdr and "shards" in hdr

    # signature verifies
    sig = bytes.fromhex(hdr["sig"])
    pub = bytes.fromhex(hdr["sig_key_id"])
    header_for_verify = dict(hdr)            # shallow copy
    header_for_verify.pop("sig")
    header_for_verify.pop("sig_key_id")
    blob = json.dumps(header_for_verify, sort_keys=True).encode() + body

