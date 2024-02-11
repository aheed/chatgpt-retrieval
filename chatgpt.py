import os
import sys

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL

import constants

os.environ["OPENAI_API_KEY"] = constants.OPENAI_KEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("data/", "**/*.py")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

portkeyHeaders = createHeaders(
    provider="openai",
    api_key=f"{constants.PORTKEY_KEY}"
)

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo", base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
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
