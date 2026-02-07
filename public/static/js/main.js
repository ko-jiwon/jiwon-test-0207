let currentData = null;
let selectedKeyword = null;

// 검색 실행
async function searchNews() {
    const keyword = document.getElementById('keywordInput').value.trim();
    
    if (!keyword) {
        alert('검색 키워드를 입력해주세요.');
        return;
    }
    
    // UI 초기화
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ keyword: keyword })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '검색 중 오류가 발생했습니다.');
        }
        
        currentData = data;
        displayResults(data);
        
    } catch (error) {
        document.getElementById('error').textContent = error.message;
        document.getElementById('error').classList.remove('hidden');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

// Enter 키로 검색
document.getElementById('keywordInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchNews();
    }
});

// 결과 표시
function displayResults(data) {
    // 키워드 필터 표시
    displayKeywordFilters(data.keywords);
    
    // 뉴스 기사 표시
    displayArticles(data.articles);
    
    // 핵심 주제 표시
    document.getElementById('mainTopic').textContent = data.main_topic;
    
    // 콘텐츠 표시
    document.getElementById('blogPost').textContent = data.blog_post;
    document.getElementById('threadContent').textContent = data.thread_content;
    displayCardnews(data.cardnews);
    
    // 결과 섹션 표시
    document.getElementById('results').classList.remove('hidden');
}

// 키워드 필터 표시
function displayKeywordFilters(keywords) {
    const container = document.getElementById('keywordFilters');
    container.innerHTML = '';
    
    // 전체 보기 버튼 추가
    const allBtn = document.createElement('button');
    allBtn.className = 'keyword-tag active';
    allBtn.textContent = '전체 보기';
    allBtn.onclick = () => filterByKeyword(null);
    container.appendChild(allBtn);
    
    // 키워드 버튼 추가
    keywords.forEach(keyword => {
        const btn = document.createElement('button');
        btn.className = 'keyword-tag';
        btn.textContent = keyword;
        btn.onclick = () => filterByKeyword(keyword);
        container.appendChild(btn);
    });
}

// 키워드로 필터링
function filterByKeyword(keyword) {
    selectedKeyword = keyword;
    
    // 버튼 활성화 상태 업데이트
    document.querySelectorAll('.keyword-tag').forEach(btn => {
        btn.classList.remove('active');
        if ((keyword === null && btn.textContent === '전체 보기') || 
            (keyword !== null && btn.textContent === keyword)) {
            btn.classList.add('active');
        }
    });
    
    // 기사 필터링
    const articles = document.querySelectorAll('.article-card');
    let visibleCount = 0;
    
    articles.forEach(article => {
        if (keyword === null) {
            article.classList.remove('hidden');
            visibleCount++;
        } else {
            const keywords = article.dataset.keywords || '';
            if (keywords.includes(keyword)) {
                article.classList.remove('hidden');
                visibleCount++;
            } else {
                article.classList.add('hidden');
            }
        }
    });
    
    document.getElementById('articleCount').textContent = visibleCount;
}

// 뉴스 기사 표시
function displayArticles(articles) {
    const container = document.getElementById('articlesList');
    container.innerHTML = '';
    
    articles.forEach((article, index) => {
        const card = document.createElement('div');
        card.className = 'article-card';
        card.dataset.keywords = article.keywords.join(',');
        
        const title = document.createElement('div');
        title.className = 'article-title';
        const titleLink = document.createElement('a');
        titleLink.href = article.link;
        titleLink.target = '_blank';
        titleLink.textContent = `${index + 1}. ${article.title}`;
        title.appendChild(titleLink);
        
        const summary = document.createElement('div');
        summary.className = 'article-summary';
        summary.textContent = article.summary;
        
        const keywords = document.createElement('div');
        keywords.className = 'article-keywords';
        article.keywords.forEach(keyword => {
            const badge = document.createElement('span');
            badge.className = 'keyword-badge';
            badge.textContent = `#${keyword}`;
            keywords.appendChild(badge);
        });
        
        card.appendChild(title);
        card.appendChild(summary);
        card.appendChild(keywords);
        container.appendChild(card);
    });
    
    document.getElementById('articleCount').textContent = articles.length;
}

// 카드뉴스 표시
function displayCardnews(cardnews) {
    const container = document.getElementById('cardnews');
    container.innerHTML = '';
    
    cardnews.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'cardnews-card';
        
        const title = document.createElement('div');
        title.className = 'cardnews-title';
        title.textContent = card.title || `카드 ${index + 1}`;
        
        const content = document.createElement('div');
        content.className = 'cardnews-content';
        content.textContent = card.content || '';
        
        cardElement.appendChild(title);
        cardElement.appendChild(content);
        container.appendChild(cardElement);
    });
}

// 클립보드에 복사
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        alert('클립보드에 복사되었습니다!');
    }).catch(err => {
        console.error('복사 실패:', err);
        alert('복사에 실패했습니다.');
    });
}

