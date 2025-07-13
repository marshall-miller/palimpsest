from langchain.callbacks.base import BaseCallbackHandler
from palobserver.bundle import build_bundle
from palobserver.ledger import write as write_ledger

class PalObserverCallback(BaseCallbackHandler):
    """Simple one-shot observer that records a bundle per LangChain call."""
    def __init__(self, key_path="observer.pem"):
        self.key_path = key_path
        self._docs = None

    # called after retrieval
    def on_retriever_end(self, documents, **kwargs):
        self._docs = documents   # store for later

    # called after chain finished (prompt built)
    def on_chain_end(self, outputs, **kwargs):
        if self._docs:
            bundle, _ = build_bundle(self._docs, self.key_path)
            write_ledger(bundle)
            print("Palimpsest bundle", bundle["bundle_id"],
                  "conflicts:", sum(len(s["flags"]) for s in bundle["shards"]))
            self._docs = None


