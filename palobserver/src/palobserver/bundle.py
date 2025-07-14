import uuid
import json
import gzip
from datetime import datetime, timezone
from pathlib import Path

from palobserver.crypto import digest, sign
from palobserver.rules import flags, extracts


def build_bundle(docs, key_path="observer.pem"):
    """
    Build a Signed Context Bundle (SCB) from document shards.

    Args:
      docs: iterable of objects with
            .page_content (str) and .metadata (dict with 'token_count', 'score').
      key_path: path to the private signing key (PEM file).

    Returns:
      headers (dict): metadata + signatures
      body_bytes (bytes): gzipped concatenation of shards
    """
    body_parts = []
    shard_meta = []
    net_vals = set()

    # 1) Process each shard
    for idx, doc in enumerate(docs):
        sid = f"sh-{idx:04x}"
        text = doc.page_content

        # add to the bundle body (with a delimiter)
        body_parts.append(f"<<<{sid}>>>\n{text}")

        # gather shard-level flags and extract Net-X values
        shard_flags = flags(text)
        extras = extracts(text)
        net_vals.update(extras.get("net_days", []))

        # record metadata for this shard
        shard_meta.append({
            "id": sid,
            "src_hash": digest(text.encode()).hex(),
            "tokens": doc.metadata.get("token_count", 0),
            "score": doc.metadata.get("score", 0),
            "flags": shard_flags,
            "position": idx,
        })

    # compress the full bundle body
    body_bytes = gzip.compress("\n".join(body_parts).encode())

    # 2) Determine bundle-level flags
    bundle_flags = []
    if len(net_vals) > 1:
        bundle_flags.append("payment_terms_mismatch")

    # 3) Build the header
    headers = {
        "@context": "https://palimpsest.dev/scb/v0.1",
        "bundle_id": uuid.uuid4().hex,
        "created": datetime.now(timezone.utc).isoformat(),
        "window_tokens": sum(m["tokens"] for m in shard_meta),
        "shards": shard_meta,
        "bundle_flags": bundle_flags,
        "body_sha256": digest(body_bytes).hex(),
    }

    # 4) Sign the bundle (header + body)
    blob = json.dumps(headers, sort_keys=True).encode() + body_bytes
    sig, pub = sign(blob, key_path)
    headers["sig"] = sig.hex()
    headers["sig_key_id"] = pub.hex()

    return headers, body_bytes

