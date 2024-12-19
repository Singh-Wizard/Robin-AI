import os
from dotenv import load_dotenv
import faiss
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
faiss_index = faiss.IndexFlatL2(len(embedding_model.embed_query("Hello")))

general_prompt = PromptTemplate.from_template(
    '''Your name is Robin-AI.
You are a friendly and concise AI assistant.
When answering questions, be brief and to the point, while maintaining a warm and friendly tone.
If personal information is shared, simply respond naturally without divulging any details unless explicitly asked.
Always prioritize clarity and be concise like a helpful friend.

Question:'''
)

context_prompt = PromptTemplate.from_template(
    '''Your name is Robin-AI.
You are a friendly AI assistant with a warm demeanor.
You are provided with detailed context. Please answer the following question using **only** the information from the provided context. Do not include any external information, assumptions, or general knowledge.
If personal information is shared, respond naturally, but do not reveal or share any personal details unless specifically asked.
Answer in a friendly and brief manner, like a good friend.

CONTEXT: """\n{context}\n"""
Question:
'''
)

def save_uploaded_file(upload_file):
    # Save the file to a local directory
    local_file_path = "_storage/"+upload_file.name
    with open(local_file_path, "wb") as f:
        f.write(upload_file.getbuffer())
    return local_file_path

def build_db_from_url(url):
    print(InMemoryDocstore())
    vectordb = FAISS(
        index=faiss_index,
        embedding_function=embedding_model,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    docs = splitter.split_documents(WebBaseLoader(url).load())
    vectordb = vectordb.from_documents(documents=docs, embedding=embedding_model)
    return vectordb

def build_db_from_pdf(file):
    file = save_uploaded_file(file)
    vectordb = FAISS(
        index=faiss_index,
        embedding_function=embedding_model,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    docs = splitter.split_documents(PyPDFLoader(file).load())
    vectordb = vectordb.from_documents(documents=docs, embedding=embedding_model)
    return vectordb

def find_context_question(question, vectordb):
    similar_docs = vectordb.similarity_search(question, k=4)
    context = ""
    for doc in similar_docs:
        context += doc.page_content + " "
    return context
