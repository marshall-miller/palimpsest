"""
Palimpsest-Observer demo:
• builds a Signed Context Bundle from two docs
• writes it to ~/.pal_ledger.db
• shows the flagged conflict
"""

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from palobserver.bundle import build_bundle
from palobserver.ledger import write as write_ledger

# ------------------------------------------------------------------ config
query = "Summarize any conflicting payment terms."

docs_raw = [
    "The invoice terms are Net-30.",                   # shard 0
    "The agreement states payments must be Net-45.",   # shard 1
    "Unrelated document text."                         # filler
]

# ------------------------------------------------------------------ embed & store
splitter = RecursiveCharacterTextSplitter(chunk_size=200)
texts = sum([splitter.split_text(t) for t in docs_raw], [])
emb = OpenAIEmbeddings()          # needs OPENAI_API_KEY env var
vs = FAISS.from_texts(texts, emb)
retriever = vs.as_retriever(search_kwargs={"k": 3})

# ------------------------------------------------------------------ observer
docs = retriever.invoke(query)            # (new API – no deprecation)
hdr, body = build_bundle(docs)
write_ledger(hdr)
print("Palimpsest bundle", hdr["bundle_id"],
      "conflicts:", sum(len(s["flags"]) for s in hdr["shards"]))

# ------------------------------------------------------------------ QA chain
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
print(chain.invoke({"query": query})["result"])

