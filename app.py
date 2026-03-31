import streamlit as st
import feedparser
from datetime import datetime
import openai
from urllib.parse import quote

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="FO Global Intelligence", page_icon="🏦", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ Intelligence Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    news_count = st.slider("가져올 뉴스 개수", 3, 15, 8)
    st.info("""
    **분석 타겟:**
    - Global IBs (JPM, GS, MS, UBS, Pictet 등)
    - 주요 Family Office 사례 연구
    """)

st.title("🏦 Family Office Global Strategy Dashboard")
st.subheader("글로벌 금융사 동향 및 패밀리 오피스 사례 분석")
st.divider()

# 2. 뉴스 크롤링 함수 (고급 필터링 적용)
def get_news(keyword):
    # 주요 금융사 키워드 조합
    banks = '(JPMorgan OR "Goldman Sachs" OR "Morgan Stanley" OR UBS OR Pictet OR "HSBC" OR "Citi Private Bank" OR "Bank of America")'
    full_query = f'({keyword}) AND {banks}'
    encoded_query = quote(full_query)
    
    # 최근 7일, 글로벌 영어 뉴스 기준
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    return feed.entries[:news_count]

# 3. AI 심층 분석 함수
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 AI 분석이 표시됩니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 글로벌 초고액자산가(UHNWI) 및 패밀리 오피스 전략 컨설턴트입니다. 
    다음 뉴스를 분석하여 전문적인 한국어 보고서를 작성하세요.

    뉴스 제목: {title}

    [작성 가이드라인]
    1. 요약 (Detailed Summary): 뉴스 내용을 핵심 위주로 5~7문장으로 상세히 요약하세요. 
    2. 시사점 (Strategic Insights): 패밀리 오피스의 자산 배분, 리스크 관리, 가업 승계 측면에서의 전략적 시사점 2-3가지를 제시하세요.
    3. 패밀리 오피스 프로필 (Family Office Profile): 
       - 만약 기사에 특정 가문이나 패밀리 오피스(예: Patel, Callan, Cascade 등)가 언급되었다면, 해당 조직의 '본사 위치, 설립 연혁, 추정 운용자산(AUM), 주요 투자 성향'에 대해 당신이 알고 있는 정보를 포함하여 표 형식이나 리스트로 설명하세요. 언급이 없다면 이 항목은 생략하세요.

    언어: 한국어
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # 더 정교한 분석을 위해 gpt-4o 권장 (비용 절감 원할 시 gpt-4o-mini 유지)
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류가 발생했습니다: {str(e)}"

# 4. 메인 실행 로직
if st.button('🚀 글로벌 금융 동향 및 FO 사례 분석 시작'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner('글로벌 금융 네트워크에서 최신 정보를 추출 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("조건에 맞는 최신 뉴스가 없습니다. 키워드를 확장하여 다시 검색합니다.")
                # 필터 없이 일반 검색 시도
                news_items = get_news("family office")
            
            for item in news_items:
                with st.expander(f"📌 {item.title}", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"**원문 확인**")
                        st.write(f"[기사 링크 클릭]({item.link})")
                        published = getattr(item, 'published', '날짜 정보 없음')
                        st.caption(f"발행일: {published}")
                        st.divider()
                        st.info("💡 **금융사/가문 식별 중...**")
                    
                    with col2:
                        analysis = analyze_article(item.title, item.link)
                        st.markdown(analysis)
                    
                    st.divider()
else:
    st.info("버튼을 누르면 JPMorgan, UBS, Goldman Sachs 등 주요 금융사의 패밀리 오피스 리포트 및 실제 가문 사례를 분석합니다.")
