from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, OpenAI, ChatOpenAI
from langchain.chains import RetrievalQA
from palobserver.callback import PalObserverCallback


# --- sample corpus ---
docs = [
    "The invoice terms are Net-30.",
    "The agreement states that payments must be Net-45.",
    "Unrelated document text."
]

# split & embed
splitter = RecursiveCharacterTextSplitter(chunk_size=200)
texts = sum([splitter.split_text(t) for t in docs], [])
emb = OpenAIEmbeddings()           # needs OPENAI_API_KEY env var
vs = FAISS.from_texts(texts, emb)

retriever = vs.as_retriever(search_kwargs={"k":3})

query = "Summarize any conflicting payment terms."

# 1) Fetch docs ourselves
docs = retriever.get_relevant_documents(query)

# 2) Build & store bundle
from palobserver.bundle import build_bundle
from palobserver.ledger import write as write_ledger

hdr, _ = build_bundle(docs)
write_ledger(hdr)
print("Palimpsest bundle", hdr["bundle_id"],
      "conflicts:", sum(len(s["flags"]) for s in hdr["shards"]))

# 3) Run the QA chain to generate the answer
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
print(chain.invoke({"query": query})["result"])

