import os
from openai import OpenAI
from dotenv import load_dotenv
from reviews.models import Review

load_dotenv()

class ChatbotService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_reviews_context(self):
        """내 리뷰 데이터를 컨텍스트로 변환"""
        reviews = Review.objects.all()[:20]
        context = "내가 본 영화 리뷰 목록:\n\n"
        
        for review in reviews:
            context += f"- 제목: {review.title}\n"
            context += f"  개봉년도: {review.release_year}년\n"
            context += f"  장르: {review.genre}\n"
            context += f"  별점: {review.rating}/10\n"
            context += f"  감독: {review.director}\n"
            context += f"  주연: {review.main_actor}\n"
            context += f"  리뷰: {review.review_content[:100]}...\n\n"
        
        return context
    
    def chat(self, user_message, conversation_history=None):
        """RAG 기반 챗봇 응답"""
        if conversation_history is None:
            conversation_history = []
        
        # 시스템 프롬프트 + RAG 컨텍스트
        context = self.get_reviews_context()
        system_prompt = f"""당신은 영화 추천 전문가입니다. 
사용자의 영화 취향을 분석하고 적절한 영화를 추천해주세요.
아래는 사용자가 본 영화 리뷰 데이터입니다:

{context}

이 데이터를 기반으로 사용자의 질문에 친절하고 구체적으로 답변해주세요."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        
        return assistant_message