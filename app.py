from flask import Flask, render_template, request, jsonify
from crawler import NewsCrawler
from analyzer import NewsAnalyzer
from content_generator import ContentGenerator
import json
import os

app = Flask(__name__)

# Vercel 환경에서 정적 파일 경로 설정
if os.environ.get('VERCEL'):
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_news():
    try:
        data = request.json
        keyword = data.get('keyword', '')
        
        if not keyword:
            return jsonify({'error': '키워드를 입력해주세요.'}), 400
        
        # 뉴스 크롤링
        crawler = NewsCrawler()
        articles = crawler.crawl_naver_news(keyword, max_articles=10)
        
        if not articles:
            return jsonify({'error': '뉴스 기사를 찾을 수 없습니다.'}), 404
        
        # 기사 분석
        analyzer = NewsAnalyzer()
        analyzed_articles = analyzer.analyze_articles(articles)
        
        # 핵심 주제 추출
        main_topic = analyzer.extract_main_topic(analyzed_articles)
        
        # 콘텐츠 생성
        generator = ContentGenerator()
        blog_post = generator.generate_blog_post(analyzed_articles, main_topic)
        thread_content = generator.generate_thread_content(analyzed_articles, main_topic)
        cardnews = generator.generate_cardnews_content(analyzed_articles, main_topic)
        
        # 모든 키워드 수집
        all_keywords = []
        for article in analyzed_articles:
            all_keywords.extend(article.get('keywords', []))
        
        # 중복 제거 및 정렬
        unique_keywords = sorted(list(set(all_keywords)))
        
        return jsonify({
            'articles': analyzed_articles,
            'keywords': unique_keywords,
            'main_topic': main_topic,
            'blog_post': blog_post,
            'thread_content': thread_content,
            'cardnews': cardnews
        })
        
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)

