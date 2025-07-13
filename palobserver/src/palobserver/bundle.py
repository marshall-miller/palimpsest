import uuid, json, gzip
from datetime import datetime, timezone
from pathlib import Path
from palobserver.crypto import digest, sign
from palobserver.rules import flags

def build_bundle(docs, key_path="observer.pem"):
    """
    docs: iterable of objects with .page_content (str) and .metadata (dict)
    returns: (headers_dict, body_bytes)
    """
    body_parts = []
    shard_meta = []

    for idx, doc in enumerate(docs):
        sid = f"sh-{idx:04x}"
        text = doc.page_content
        body_parts.append(f"<<<{sid}>>>\n{text}")

        shard_meta.append({
            "id": sid,
            "src_hash": digest(text.encode()).hex(),
            "tokens": doc.metadata.get("token_count", 0),
            "score": doc.metadata.get("score", 0),
            "flags": flags(text),
            "position": idx,
        })

    body_bytes = gzip.compress("\n".join(body_parts).encode())

    headers = {
        "@context": "https://palimpsest.dev/scb/v0.1",
        "bundle_id": uuid.uuid4().hex,
        "created": datetime.now(timezone.UTC).isoformat(),
        "window_tokens": sum(m["tokens"] for m in shard_meta),
        "shards": shard_meta,
        "body_sha256": digest(body_bytes).hex(),
    }

    blob = json.dumps(headers, sort_keys=True).encode() + body_bytes
    sig, pub = sign(blob, key_path)
    headers["sig"] = sig.hex()
    headers["sig_key_id"] = pub.hex()

    return headers, body_bytes

