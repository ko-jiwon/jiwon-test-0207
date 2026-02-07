import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import time

class NewsCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_naver_news(self, keyword: str, max_articles: int = 10) -> List[Dict]:
        """
        네이버 뉴스에서 키워드로 검색하여 뉴스 기사 크롤링
        """
        articles = []
        search_url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_jum"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 검색 결과에서 링크 추출
            news_items = soup.select('div.news_area')[:max_articles]
            
            for item in news_items:
                try:
                    # 제목과 링크 추출
                    title_elem = item.select_one('a.news_tit')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 기사 본문 크롤링
                    article_content = self._crawl_article_content(link)
                    
                    if article_content:
                        articles.append({
                            'title': title,
                            'link': link,
                            'content': article_content
                        })
                    
                    time.sleep(0.5)  # 서버 부하 방지
                    
                    if len(articles) >= max_articles:
                        break
                        
                except Exception as e:
                    print(f"기사 크롤링 중 오류: {e}")
                    continue
            
            # 기사가 부족한 경우 추가 검색
            if len(articles) < max_articles:
                news_links = soup.select('a.info')[:max_articles - len(articles)]
                for link_elem in news_links:
                    if len(articles) >= max_articles:
                        break
                    try:
                        link = link_elem.get('href', '')
                        if link and link not in [a['link'] for a in articles]:
                            article_content = self._crawl_article_content(link)
                            if article_content:
                                title = link_elem.get_text(strip=True) or "제목 없음"
                                articles.append({
                                    'title': title,
                                    'link': link,
                                    'content': article_content
                                })
                            time.sleep(0.5)
                    except:
                        continue
            
        except Exception as e:
            print(f"뉴스 검색 중 오류: {e}")
        
        return articles[:max_articles]
    
    def _crawl_article_content(self, url: str) -> str:
        """
        개별 기사 본문 크롤링
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 뉴스 본문
            content = soup.select_one('#articleBodyContents, .article_body, .article-body, .articleBody')
            if content:
                # 스크립트와 스타일 제거
                for script in content(["script", "style"]):
                    script.decompose()
                text = content.get_text(separator=' ', strip=True)
                # 공백 정리
                text = re.sub(r'\s+', ' ', text)
                return text[:5000]  # 최대 5000자
            
            # 다른 뉴스 사이트 대응
            content = soup.select_one('article, .article-content, .content, .news-content')
            if content:
                for script in content(["script", "style"]):
                    script.decompose()
                text = content.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text)
                return text[:5000]
            
            # 기본 본문 추출
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            text = re.sub(r'\s+', ' ', text)
            return text[:5000] if text else ""
            
        except Exception as e:
            print(f"본문 크롤링 오류 ({url}): {e}")
            return ""

