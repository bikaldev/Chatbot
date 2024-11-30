import os
import PyPDF2

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableMap
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class RAGChain:
    def __init__(self):
        self.host =  os.getenv('QDRANT_HOST') if(os.getenv('QDRANT_HOST')) else 'localhost'
        self.port = os.getenv('QDRANT_PORT') if(os.getenv('QDRANT_PORT')) else '6333'
        self.embeddings = self._init_embeddings()
        self._init_chain()
        self.vectorstore = self._init_vectorstore()

    def _init_chain(self, ):
        template = """You are a helpful AI assistant and will answer the following questions based on the provided context. If the context has nothing to do with the question, answer it normally.
        \nQuestion: {question} \nContext: {context}"""

        prompt = PromptTemplate.from_template(template)

        llm = ChatGroq(
            model='llama3-70b-8192',
            temperature=0.0,
            max_retries=2
        )

        # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.rag_chain = RunnableMap({
            "question": lambda x: x["question"],
            "context": lambda x: x["retriever"].invoke(x["question"]),
        }) | prompt | llm
    
    def _init_embeddings(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.embedding_dim = len(embeddings.embed_query("Test"))
        return embeddings

    def _init_vectorstore(self):
        client = QdrantClient(host = self.host, port = self.port, timeout=50)

        if not client.collection_exists('session_collection'):
            client.create_collection(
                collection_name='session_collection',
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
            )

        return QdrantVectorStore(client = client, embedding=self.embeddings, collection_name= "session_collection")

    def _ingest_document(self, file):
            if file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            elif file.type.startswith("text/"):
                return file.read().decode("utf-8")
            return None

    # Embedding Document
    def _embed_document(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        self.vectorstore.add_documents([Document(page_content=chunk) for chunk in chunks])
    

    def add_to_vectorstore(self, file):
        text = self._ingest_document(file)
        self._embed_document(text)
    
    def run(self, input):
        response = self.rag_chain.invoke({
            'question': input,
            'retriever': self.vectorstore.as_retriever(search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},)
        })
        return response
