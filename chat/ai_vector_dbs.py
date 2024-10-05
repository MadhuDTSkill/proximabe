from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class AIVectorDB:
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        self.embedder = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        self.root_path = 'vector_dbs/'
        
    def load_text_documents(self, file_path) -> list:
        # Determine the file type
        file_extension = file_path.split('.')[-1].lower()
        if file_extension == 'txt':
            documents = TextLoader(file_path).load()
        elif file_extension == 'pdf':
            documents = PyPDFLoader(file_path).load_and_split()
        else:
            raise ValueError("Unsupported file type.")

        return documents

    def split_documents(self, documents: list) -> list:
        return self.text_splitter.split_documents(documents)
    
    def get_vector_db(self, documents: list):
        return FAISS.from_documents(documents, self.embedder)
    
    def save_vector_db(self, file_path : str, user_id:str, chat_id:str) -> None:
        documents = self.load_text_documents(file_path)
        documents = self.split_documents(documents)
        vector_db = self.get_vector_db(documents)
        save_path = self.root_path + user_id + "/" + chat_id + '/faiss_index'
        vector_db.save_local(save_path)
        return save_path
        
    def load_vector_db(self, vector_db_path) -> None:
        return FAISS.load_local(vector_db_path, self.embedder, allow_dangerous_deserialization=True)
    
    
    def get_context(self, vector_db_path:str, query:str) -> str:
        vector_db = self.load_vector_db(vector_db_path)
        docs = vector_db.similarity_search_with_score(query)
        if docs and len(docs) > 0:
            return docs[0][0].page_content
        return None