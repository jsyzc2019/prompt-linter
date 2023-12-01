import os

from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms.openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from datasets import load_dataset

ASTRA_DB_SECURE_BUNDLE_PATH = os.environ['ASTRA_DB_SECURE_BUNDLE_PATH']
ASTRA_DB_APPLICATION_TOKEN = os.environ['ASTRA_DB_APPLICATION_TOKEN']
ASTRA_DB_CLIENT_ID = os.environ['ASTRA_DB_CLIENT_ID']
ASTRA_DB_CLIENT_SECRET = os.environ['ASTRA_DB_CLIENT_SECRET']
ASTRA_DB_KEYSPACE = os.environ['ASTRA_DB_KEYSPACE']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

cloud_config = {
    'secure_connect_bundle': ASTRA_DB_SECURE_BUNDLE_PATH,
}
auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
astraSession = cluster.connect()

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
myEmbedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

myCassandraVStore = Cassandra(
    embedding = myEmbedding,
    session = astraSession,
    keyspace = ASTRA_DB_KEYSPACE,
    table_name = "qa_mini_demo",
)

print("Loading data from huggingface...")
myDataset = load_dataset("Biddls/Onion_News", split="train")
headlines = myDataset["text"][:50]

print("Generating embeddings and storing in AstraDB...")
myCassandraVStore.add_texts(headlines)

print(f"Inserted {len(headlines)} headlines.")

vectorIndex = VectorStoreIndexWrapper(vectorstore=myCassandraVStore)

first_question = True
while True:
    if first_question:
        query_text = input("Enter your question (or type 'quit' to exit): ")
        first_question = False
    else:
        query_text = input("What's your next question (or type 'quit' to exit): ")

    if query_text.lower() == 'quit':
        break

    print(f"QUESTION: {query_text}")
    answer = vectorIndex.query(query_text, llm=llm).strip()
    print(f"ANSWER: {answer}")

    print("DOCUMENTS BY RELEVANCE:")
    for doc, score in myCassandraVStore.similarity_search_with_score(query_text, k=4):
        print(" %0.4f \" %s ...\"" % (score, doc.page_content[:60]))