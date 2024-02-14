import os
import sys

from langchain.chains import ConversationalRetrievalChain
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import RecursiveCharacterTextSplitter
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from pymongo import MongoClient
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

import constants

os.environ["OPENAI_API_KEY"] = constants.OPENAI_KEY

MONGODB_ATLAS_CLUSTER_URI = constants.MONGODB_CLUSTER_URI

client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

DB_NAME = "ragdb"
COLLECTION_NAME = "ragcollection"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "index_name"

database = client[DB_NAME]
collectionExists = COLLECTION_NAME in database.list_collection_names()
if not collectionExists:
  print(f"No such collection: db={DB_NAME} collection={COLLECTION_NAME}")
  exit(1)
  
print("Collection found")
coll = database[COLLECTION_NAME]

query = None
rebuild_db = False
if len(sys.argv) > 1:
  query = sys.argv[1]

  if len(sys.argv) > 2:
    rebuild_db = sys.argv[2] == "-d"


if rebuild_db:
  print("rebuilding vector DB")
  
  coll.delete_many({}) # remove any existing document from the collection

  loader = DirectoryLoader("data/", "**/*.py")
  data = loader.load()
  print(f"loaded {len(data)} documents")
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
  docs = text_splitter.split_documents(data)
  print(f"split into {len(docs)} chunks")

  vector_search = MongoDBAtlasVectorSearch.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(disallowed_special=()),
    collection=coll,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
  )
else:
  print("opening existing vector DB")
  vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_ATLAS_CLUSTER_URI,
    DB_NAME + "." + COLLECTION_NAME,
    OpenAIEmbeddings(disallowed_special=()),
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
  )

print(f"documents in DB: {coll.count_documents({})}")
  

portkeyHeaders = createHeaders(
    provider="openai",
    api_key=f"{constants.PORTKEY_KEY}"
)

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo", base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders),
  retriever=vector_search.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
while True:
  if not query:
    print("Prompt: ")
    query = input()
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None

"""
Why use LCEL ?
https://python.langchain.com/docs/expression_language/why
Is it not just reinventing ReactiveX? (RxPY/rxjs)
  It is tempting to recreate the LCEL examples on the page with RxPY.
Another thing I don't like about Langchain: it hides stuff behind magic => harder to understand the concepts

Interesting project:
https://github.com/rogeriochaves/langstream?tab=readme-ov-file
I like the light weight approach, but I think it should be RxPY, not a home made stream class.

"""
