import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config.agent_config import AgentConfig

class WebScraper:
    """웹 스크래핑 유틸리티 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': AgentConfig.USER_AGENT
        })
        self.driver = None
        
    def setup_selenium(self):
        """Selenium 웹드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-agent={AgentConfig.USER_AGENT}')
        
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=chrome_options
        )
        
    def close_selenium(self):
        """Selenium 웹드라이버 종료"""
        if self.driver:
            self.driver.quit()
            
    def scrape_with_requests(self, url):
        """requests를 사용한 기본 스크래핑"""
        try:
            response = self.session.get(url, timeout=AgentConfig.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 메타데이터 추출
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # 메타 설명 추출
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # 본문 텍스트 추출
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
                
            # 주요 콘텐츠 영역 찾기
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post'))
            
            if main_content:
                text_content = main_content.get_text(separator=' ', strip=True)
            else:
                text_content = soup.get_text(separator=' ', strip=True)
                
            # 텍스트 정리
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content[:AgentConfig.MAX_CONTENT_LENGTH]
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'content': text_content,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
            
    def scrape_with_selenium(self, url):
        """Selenium을 사용한 동적 콘텐츠 스크래핑"""
        if not self.driver:
            self.setup_selenium()
            
        try:
            self.driver.get(url)
            
            # 페이지 로딩 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 스크롤하여 동적 콘텐츠 로드
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 메타데이터 추출
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # 본문 텍스트 추출
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
                
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post'))
            
            if main_content:
                text_content = main_content.get_text(separator=' ', strip=True)
            else:
                text_content = soup.get_text(separator=' ', strip=True)
                
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content[:AgentConfig.MAX_CONTENT_LENGTH]
            
            return {
                'url': url,
                'title': title_text,
                'content': text_content,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
            
    def search_websites(self, query, max_results=5):
        """검색 쿼리를 기반으로 관련 웹사이트 찾기"""
        # Google 검색 시뮬레이션 (실제로는 검색 API 사용 권장)
        search_urls = [
            f"https://www.google.com/search?q={query}",
            f"https://www.bing.com/search?q={query}",
            f"https://duckduckgo.com/?q={query}"
        ]
        
        found_urls = []
        
        for search_url in search_urls[:1]:  # Google만 사용
            try:
                response = self.session.get(search_url, timeout=AgentConfig.REQUEST_TIMEOUT)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 검색 결과 링크 추출 (실제 구현에서는 더 정교한 파싱 필요)
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link['href']
                    if href.startswith('http') and 'google.com' not in href:
                        found_urls.append(href)
                        if len(found_urls) >= max_results:
                            break
                            
            except Exception as e:
                print(f"검색 중 오류: {e}")
                
        return found_urls[:max_results]
        
    def scrape_multiple_sites(self, urls):
        """여러 사이트 스크래핑"""
        results = []
        
        for url in urls:
            print(f"스크래핑 중: {url}")
            
            # 먼저 requests로 시도
            result = self.scrape_with_requests(url)
            
            # 실패하면 Selenium으로 시도
            if result['status'] == 'error':
                result = self.scrape_with_selenium(url)
                
            results.append(result)
            time.sleep(1)  # 요청 간격 조절
            
        return results 