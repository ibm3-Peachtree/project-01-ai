import os
from dotenv import load_dotenv
import base64

from schemas.faq import *

from llama_index.core import (
    VectorStoreIndex, StorageContext, 
    load_index_from_storage, Settings, 
    Document
)
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import PromptTemplate
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

# from google import genai
# from google.genai.errors import ServerError

load_dotenv()

Settings.llm = Gemini(model="models/gemini-2.5-flash")
Settings.embed_model = HuggingFaceEmbedding(model_name="BM-K/KoSimCSE-roberta")

class RAGService :
    def __init__(self, persist_dir="./storage") :
        self.persist_dir = persist_dir

        # 1. 디렉터리가 없으면 자동 생성 (테스트 시 에러 방지)
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
            print(f"디렉터리 생성: {self.persist_dir}")

        # 2. 저장된 파일 존재 여부 확인
        if os.listdir(self.persist_dir): 
            try:
                # load saved storage context
                storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                # load saved index
                self.index = load_index_from_storage(storage_context)
                print("기존 인덱스 로드 완료.")
            except Exception as e:
                print(f"인덱스 로드 실패, 새로 생성합니다: {e}")
                # initialize
                self.index = VectorStoreIndex([])
        else:
            # 처음 실행 시 빈 인덱스 생성
            self.index = VectorStoreIndex([])
            print("새 인덱스를 생성합니다.")

        faq_prompt = PromptTemplate(
            """
            "당신은 제공된 AI 포럼의 공지사항(Context) 정보를 바탕으로 사용자의 질문에 한국어로 친절하게 답변하는 AI입니다.\n"
            "답변은 공지사항의 격식에 맞춰 작성하세요. 그리고 '[AI가 생성한 답변입니다.]'를 말머리에 붙여주세요.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "질문: {query_str}\n"
            "답변: "
            """
        )
        self.query_engine = self.index.as_query_engine(
            text_qa_template=faq_prompt
        )
        

    def add_document(self, data : FAQData) :
        '''
        [공지사항 저장]
        add_document 호출 시 index.insert()를 사용하면 메모리 상의 인덱스가 업데이트되고, 
        그 즉시 persist()를 호출하여 디스크에 동기화하므로 데이터의 일관성을 유지할 수 있습니다.
        '''
        decoded_content = base64.b64decode(data.content).decode('utf-8')
        new_doc = Document(text=decoded_content, metadata={"title" : data.title, "notice_id" : data.notice_id})
        self.index.insert(new_doc)

        self.index.storage_context.persist(persist_dir="./storage")

    def generate_answer(self, title : str, content : str) :
        """
        title : 질문 제목
        content : 질문 내용
        """
        # 프롬프트 템플릿의 변수 {title}, {content}와 일치하도록 구성합니다.
        query_str = f"제목: {title}\n내용: {content}"

        # 쿼리 엔진을 통해 답변 생성
        response = self.query_engine.query(query_str)

        return str(response)

rag_service_instance = RAGService(persist_dir="./storage")