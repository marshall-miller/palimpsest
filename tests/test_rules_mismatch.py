from types import SimpleNamespace
from palobserver.bundle import build_bundle

def test_payment_mismatch_flag(tmp_path):
    docs = [
        SimpleNamespace(page_content="Invoice says Net-30.", metadata={}),
        SimpleNamespace(page_content="Master agreement: Net-45 payment terms.", metadata={})
    ]
    # temp key
    from palobserver.crypto import generate_key
    keyfile = tmp_path / "observer.pem"
    generate_key(keyfile.as_posix())

    hdr, _ = build_bundle(docs, key_path=keyfile.as_posix())
    assert "payment_terms_mismatch" in hdr["bundle_flags"]

