import re
import json
from typing import List, Dict, Any
from config.agent_config import AgentConfig

class DataProcessor:
    """데이터 처리 유틸리티 클래스"""
    
    def __init__(self):
        self.max_length = AgentConfig.MAX_CONTENT_LENGTH
        self.summary_length = AgentConfig.SUMMARIZATION_LENGTH
        
    def clean_text(self, text: str) -> str:
        """텍스트 정리 및 정규화"""
        if not text:
            return ""
            
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 특수 문자 정리
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
        
        # 길이 제한
        if len(text) > self.max_length:
            text = text[:self.max_length] + "..."
            
        return text.strip()
        
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용 권장)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 불용어 제거
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # 단어 빈도 계산
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:max_keywords]]
        
    def summarize_text(self, text: str) -> str:
        """텍스트 요약"""
        if not text:
            return ""
            
        # 간단한 요약 (실제로는 AI 모델 사용 권장)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text
            
        # 첫 번째, 중간, 마지막 문장 선택
        summary_sentences = []
        summary_sentences.append(sentences[0])
        
        if len(sentences) > 2:
            mid_index = len(sentences) // 2
            summary_sentences.append(sentences[mid_index])
            
        summary_sentences.append(sentences[-1])
        
        summary = '. '.join(summary_sentences) + '.'
        
        if len(summary) > self.summary_length:
            summary = summary[:self.summary_length] + "..."
            
        return summary
        
    def categorize_content(self, text: str) -> str:
        """콘텐츠 카테고리 분류"""
        # 간단한 키워드 기반 분류
        text_lower = text.lower()
        
        categories = {
            'technology': ['tech', 'software', 'programming', 'ai', 'machine learning', 'data'],
            'business': ['business', 'company', 'market', 'finance', 'investment', 'startup'],
            'health': ['health', 'medical', 'disease', 'treatment', 'medicine', 'doctor'],
            'education': ['education', 'learning', 'school', 'university', 'course', 'study'],
            'news': ['news', 'report', 'announcement', 'update', 'latest'],
            'entertainment': ['entertainment', 'movie', 'music', 'game', 'sport', 'celebrity']
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
            
        if scores:
            return max(scores, key=scores.get)
        else:
            return 'general'
            
    def structure_data(self, scraped_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """스크래핑된 데이터 구조화"""
        structured_data = {
            'total_sites': len(scraped_data),
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'categories': {},
            'keywords': [],
            'summaries': [],
            'raw_data': []
        }
        
        all_keywords = []
        all_text = ""
        
        for data in scraped_data:
            if data['status'] == 'success':
                structured_data['successful_scrapes'] += 1
                
                # 텍스트 정리
                content = self.clean_text(data.get('content', ''))
                title = self.clean_text(data.get('title', ''))
                
                # 카테고리 분류
                category = self.categorize_content(content)
                structured_data['categories'][category] = structured_data['categories'].get(category, 0) + 1
                
                # 키워드 추출
                keywords = self.extract_keywords(content)
                all_keywords.extend(keywords)
                
                # 요약 생성
                summary = self.summarize_text(content)
                structured_data['summaries'].append({
                    'url': data['url'],
                    'title': title,
                    'summary': summary,
                    'category': category,
                    'keywords': keywords[:5]
                })
                
                all_text += content + " "
                
            else:
                structured_data['failed_scrapes'] += 1
                
            structured_data['raw_data'].append(data)
            
        # 전체 키워드 통계
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
        structured_data['keywords'] = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return structured_data
        
    def generate_insights(self, structured_data: Dict[str, Any]) -> List[str]:
        """데이터에서 인사이트 생성"""
        insights = []
        
        # 성공률 분석
        success_rate = structured_data['successful_scrapes'] / structured_data['total_sites'] * 100
        insights.append(f"스크래핑 성공률: {success_rate:.1f}%")
        
        # 카테고리 분석
        if structured_data['categories']:
            top_category = max(structured_data['categories'], key=structured_data['categories'].get)
            insights.append(f"주요 카테고리: {top_category}")
            
        # 키워드 분석
        if structured_data['keywords']:
            top_keywords = [kw for kw, freq in structured_data['keywords'][:5]]
            insights.append(f"주요 키워드: {', '.join(top_keywords)}")
            
        # 콘텐츠 품질 분석
        if structured_data['summaries']:
            avg_summary_length = sum(len(s['summary']) for s in structured_data['summaries']) / len(structured_data['summaries'])
            insights.append(f"평균 요약 길이: {avg_summary_length:.0f}자")
            
        return insights
        
    def format_for_report(self, structured_data: Dict[str, Any], insights: List[str]) -> Dict[str, Any]:
        """보고서용 데이터 포맷"""
        return {
            'executive_summary': {
                'total_sites_analyzed': structured_data['total_sites'],
                'successful_analyses': structured_data['successful_scrapes'],
                'success_rate': f"{structured_data['successful_scrapes'] / structured_data['total_sites'] * 100:.1f}%",
                'key_insights': insights[:3]
            },
            'detailed_analysis': {
                'category_distribution': structured_data['categories'],
                'top_keywords': structured_data['keywords'][:10],
                'content_summaries': structured_data['summaries']
            },
            'recommendations': self.generate_recommendations(structured_data, insights),
            'raw_data': structured_data['raw_data']
        }
        
    def generate_recommendations(self, structured_data: Dict[str, Any], insights: List[str]) -> List[str]:
        """데이터 기반 권장사항 생성"""
        recommendations = []
        
        # 성공률 기반 권장사항
        success_rate = structured_data['successful_scrapes'] / structured_data['total_sites']
        if success_rate < 0.7:
            recommendations.append("웹사이트 접근성 개선이 필요합니다. 더 많은 사이트에서 정보를 수집할 수 있도록 스크래핑 전략을 조정하세요.")
            
        # 카테고리 기반 권장사항
        if structured_data['categories']:
            top_category = max(structured_data['categories'], key=structured_data['categories'].get)
            recommendations.append(f"{top_category} 분야에 대한 추가 분석이 필요합니다.")
            
        # 키워드 기반 권장사항
        if structured_data['keywords']:
            recommendations.append("주요 키워드를 중심으로 더 구체적인 정보 수집이 필요합니다.")
            
        return recommendations 