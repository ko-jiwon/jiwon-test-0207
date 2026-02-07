from openai import OpenAI
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
    
    def generate_blog_post(self, articles: List[Dict], main_topic: str) -> str:
        """
        1200자 블로그 글 생성
        """
        # 기사 정보 수집
        titles = [article['title'] for article in articles]
        summaries = [article['summary'] for article in articles]
        content = "\n\n".join([f"제목: {title}\n요약: {summary}" for title, summary in zip(titles, summaries)])
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 전문 블로그 작가입니다. 독자에게 유용하고 흥미로운 내용을 작성합니다."},
                        {"role": "user", "content": f"""다음 뉴스 기사들을 종합하여 '{main_topic}'에 대한 1200자 분량의 블로그 글을 작성해주세요.

요구사항:
- 서론, 본문, 결론 구조
- 구체적인 사실과 데이터 포함
- 읽기 쉽고 매력적인 문체
- 정확히 1200자 분량

뉴스 기사 정보:
{content[:4000]}

블로그 글을 작성해주세요:"""}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                blog_content = response.choices[0].message.content.strip()
                # 1200자로 조정
                if len(blog_content) > 1200:
                    blog_content = blog_content[:1200]
                return blog_content
            except Exception as e:
                print(f"블로그 생성 API 오류: {e}")
        
        # API가 없을 때 기본 템플릿
        return self._generate_default_blog(articles, main_topic)
    
    def generate_thread_content(self, articles: List[Dict], main_topic: str) -> str:
        """
        200자 내외 스레드 콘텐츠 생성
        """
        summaries = [article['summary'] for article in articles[:3]]
        content = "\n".join(summaries)
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 소셜미디어 콘텐츠 작가입니다. 짧고 임팩트 있는 스레드 형식의 콘텐츠를 작성합니다."},
                        {"role": "user", "content": f"""'{main_topic}'에 대한 200자 내외의 짧고 임팩트 있는 스레드 콘텐츠를 작성해주세요.

요구사항:
- 핵심만 간결하게
- 독자의 관심을 끄는 문구
- 200자 내외

참고 정보:
{content[:1500]}

스레드 콘텐츠를 작성해주세요:"""}
                    ],
                    max_tokens=150,
                    temperature=0.8
                )
                thread_content = response.choices[0].message.content.strip()
                # 200자로 조정
                if len(thread_content) > 200:
                    thread_content = thread_content[:200]
                return thread_content
            except Exception as e:
                print(f"스레드 생성 API 오류: {e}")
        
        # API가 없을 때 기본 템플릿
        return self._generate_default_thread(articles, main_topic)
    
    def generate_cardnews_content(self, articles: List[Dict], main_topic: str) -> List[Dict]:
        """
        인스타그램 5장짜리 카드뉴스 콘텐츠 생성
        """
        cardnews = []
        
        if self.openai_api_key:
            try:
                summaries = [article['summary'] for article in articles]
                content = "\n".join(summaries[:5])
                
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 인스타그램 카드뉴스 콘텐츠 기획자입니다. 5장의 카드뉴스를 구성합니다."},
                        {"role": "user", "content": f"""'{main_topic}'에 대한 인스타그램 카드뉴스 5장을 기획해주세요.

각 카드별로:
1. 제목 (간결하고 임팩트 있게)
2. 본문 내용 (50-80자 내외)
3. 핵심 포인트

참고 정보:
{content[:2000]}

다음 형식으로 작성해주세요:
카드 1:
제목: [제목]
내용: [내용]

카드 2:
제목: [제목]
내용: [내용]

... (5장까지)"""}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content.strip()
                # 파싱하여 구조화
                cardnews = self._parse_cardnews(result)
                
            except Exception as e:
                print(f"카드뉴스 생성 API 오류: {e}")
        
        # API가 없거나 파싱 실패 시 기본 템플릿
        if not cardnews or len(cardnews) < 5:
            cardnews = self._generate_default_cardnews(articles, main_topic)
        
        return cardnews[:5]  # 정확히 5장
    
    def _parse_cardnews(self, text: str) -> List[Dict]:
        """카드뉴스 텍스트 파싱"""
        cards = []
        lines = text.split('\n')
        current_card = {}
        
        for line in lines:
            line = line.strip()
            if '카드' in line and ('제목' in line or '1' in line or '2' in line or '3' in line or '4' in line or '5' in line):
                if current_card:
                    cards.append(current_card)
                current_card = {}
            elif '제목:' in line or '제목 :' in line:
                current_card['title'] = line.split(':', 1)[1].strip()
            elif '내용:' in line or '내용 :' in line:
                current_card['content'] = line.split(':', 1)[1].strip()
        
        if current_card:
            cards.append(current_card)
        
        return cards if cards else []
    
    def _generate_default_blog(self, articles: List[Dict], main_topic: str) -> str:
        """기본 블로그 템플릿"""
        intro = f"최근 '{main_topic}'에 대한 뉴스가 주목받고 있습니다. "
        body = "\n\n".join([f"• {article['title']}\n  {article['summary']}" for article in articles[:5]])
        conclusion = f"\n\n이러한 동향을 보면 '{main_topic}'에 대한 관심이 지속되고 있음을 알 수 있습니다."
        return (intro + body + conclusion)[:1200]
    
    def _generate_default_thread(self, articles: List[Dict], main_topic: str) -> str:
        """기본 스레드 템플릿"""
        return f"🔥 {main_topic} 관련 최신 뉴스 요약\n\n" + "\n".join([f"• {article['title']}" for article in articles[:3]])[:200]
    
    def _generate_default_cardnews(self, articles: List[Dict], main_topic: str) -> List[Dict]:
        """기본 카드뉴스 템플릿"""
        cards = [
            {
                'title': main_topic,
                'content': f"최근 '{main_topic}' 관련 뉴스가 화제입니다."
            }
        ]
        
        for i, article in enumerate(articles[:4], 2):
            cards.append({
                'title': article['title'][:30],
                'content': article['summary'][:80]
            })
        
        # 5장이 안 되면 채우기
        while len(cards) < 5:
            cards.append({
                'title': '종합 분석',
                'content': '다양한 관점에서 살펴본 핵심 이슈입니다.'
            })
        
        return cards[:5]

