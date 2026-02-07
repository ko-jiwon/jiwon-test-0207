from typing import List, Dict
import re
from collections import Counter
from konlpy.tag import Okt
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class NewsAnalyzer:
    def __init__(self):
        try:
            self.okt = Okt()
            self.use_konlpy = True
        except Exception as e:
            print(f"KoNLPy 초기화 실패: {e}. 기본 키워드 추출 방식을 사용합니다.")
            self.okt = None
            self.use_konlpy = False
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
    
    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        뉴스 기사들을 분석하여 제목, 요약, 핵심키워드 추출
        """
        analyzed_articles = []
        
        for article in articles:
            try:
                summary = self._generate_summary(article['content'])
                keywords = self._extract_keywords(article['content'], article['title'])
                
                analyzed_articles.append({
                    'title': article['title'],
                    'link': article['link'],
                    'summary': summary,
                    'keywords': keywords,
                    'content': article['content']
                })
            except Exception as e:
                print(f"기사 분석 중 오류: {e}")
                analyzed_articles.append({
                    'title': article['title'],
                    'link': article['link'],
                    'summary': article['content'][:200] + "...",
                    'keywords': [],
                    'content': article['content']
                })
        
        return analyzed_articles
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """
        기사 내용 요약 생성 (OpenAI API 사용 또는 간단한 추출)
        """
        if not content or len(content) < 50:
            return "내용이 부족합니다."
        
        # OpenAI API가 있으면 사용
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 뉴스 기사를 요약하는 전문가입니다. 핵심 내용만 간결하게 요약해주세요."},
                        {"role": "user", "content": f"다음 뉴스 기사를 {max_length}자 이내로 요약해주세요:\n\n{content[:2000]}"}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API 오류: {e}")
        
        # API가 없으면 간단한 추출 요약
        sentences = re.split(r'[.!?]\s+', content)
        if len(sentences) <= 3:
            return content[:max_length] + "..."
        
        # 처음 2-3문장 추출
        summary = '. '.join(sentences[:3])
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        return summary
    
    def _extract_keywords(self, content: str, title: str, top_n: int = 5) -> List[str]:
        """
        핵심 키워드 추출 (KoNLPy 사용 또는 기본 방식)
        """
        # 제목과 본문 결합
        text = title + " " + content[:1000]
        
        # KoNLPy 사용 가능한 경우
        if self.use_konlpy and self.okt:
            try:
                # 명사 추출
                nouns = self.okt.nouns(text)
                
                # 불용어 제거
                stopwords = ['것', '수', '등', '및', '이', '그', '저', '때', '곳', '년', '월', '일', 
                            '때문', '경우', '이후', '이전', '중', '후', '전', '위', '아래', '쪽']
                nouns = [n for n in nouns if len(n) > 1 and n not in stopwords]
                
                # 빈도수 계산
                keyword_counts = Counter(nouns)
                keywords = [word for word, count in keyword_counts.most_common(top_n)]
                
                if keywords:
                    return keywords
            except Exception as e:
                print(f"KoNLPy 키워드 추출 오류: {e}")
        
        # 기본 키워드 추출 방식 (KoNLPy 실패 시 또는 사용 불가 시)
        words = re.findall(r'\b[가-힣]{2,}\b', text[:500])
        # 불용어 제거
        stopwords = ['것', '수', '등', '및', '이', '그', '저', '때', '곳', '년', '월', '일', 
                    '때문', '경우', '이후', '이전', '중', '후', '전', '위', '아래', '쪽', '하는', '있는', '있는', '되는']
        words = [w for w in words if w not in stopwords]
        word_counts = Counter(words)
        keywords = [word for word, count in word_counts.most_common(top_n)][:top_n]
        
        return keywords if keywords else ["키워드 없음"]
    
    def extract_main_topic(self, articles: List[Dict]) -> str:
        """
        모든 기사들을 종합하여 핵심 주제 추출
        """
        # 모든 키워드 수집
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.get('keywords', []))
        
        # 가장 빈번한 키워드 찾기
        keyword_counts = Counter(all_keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(3)]
        
        # 기사 제목과 요약을 종합
        titles = [article['title'] for article in articles]
        summaries = [article['summary'] for article in articles]
        
        combined_text = " ".join(titles) + " " + " ".join(summaries)
        
        # OpenAI API로 핵심 주제 추출
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 뉴스 기사들을 분석하여 핵심 주제를 한 문장으로 요약하는 전문가입니다."},
                        {"role": "user", "content": f"다음 뉴스 기사들의 제목과 요약을 종합하여 핵심 주제를 한 문장으로 요약해주세요:\n\n{combined_text[:3000]}"}
                    ],
                    max_tokens=100,
                    temperature=0.5
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"주제 추출 API 오류: {e}")
        
        # API가 없으면 가장 빈번한 키워드 기반 주제 생성
        if top_keywords:
            return f"{top_keywords[0]} 관련 주요 이슈 및 동향"
        return "종합 뉴스 분석"

