import streamlit as st
import feedparser
from datetime import datetime
import openai
from urllib.parse import quote

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="FO Deep Intelligence", page_icon="🏛️", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ Intelligence Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    news_count = st.slider("가져올 뉴스 개수", 3, 15, 8)
    st.info("""
    **분석 타겟:**
    - Global IBs & Private Banks (JPM, GS, UBS, Julius Baer 등)
    - Global Consulting Firms (McKinsey, BCG, Deloitte 등)
    - Family Office Governance & Asset Allocation
    """)

st.title("🏛️ Family Office & Global Finance Intelligence")
st.subheader("글로벌 금융사 및 컨설팅 펌의 패밀리 오피스 동향 분석")
st.divider()

# 2. 뉴스 크롤링 함수 (금융사 + 컨설팅 펌 통합 필터링)
def get_news(keyword):
    # 금융사 및 컨설팅 펌 키워드 대폭 확장
    entities = [
        "JPMorgan", "Goldman Sachs", "Morgan Stanley", "UBS", "Pictet", 
        "Julius Baer", "Deutsche Bank", "Barclays", "BNP Paribas", "HSBC", 
        "Nomura", "Lombard Odier", "Citi Private Bank", "McKinsey", "BCG", 
        "Bain & Company", "Deloitte", "PwC", "EY", "KPMG", "Rockefeller", "Northern Trust"
    ]
    
    # "family office"와 위 기업 중 하나라도 포함된 기사 검색
    entities_query = " OR ".join([f'"{e}"' for e in entities])
    full_query = f'({keyword}) AND ({entities_query})'
    encoded_query = quote(full_query)
    
    # 최근 7일, 글로벌 영어 뉴스 기준
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    return feed.entries[:news_count]

# 3. AI 심층 분석 함수 (분량 및 깊이 강화)
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 AI 분석이 표시됩니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    # 프롬프트: 10~15문장 요약 및 전문적 시사점 강조
    prompt = f"""
    당신은 글로벌 패밀리 오피스 및 자산관리 전략 전문가입니다. 
    다음 뉴스를 분석하여 전문적인 한국어 보고서를 작성하세요.

    뉴스 제목: {title}

    [작성 가이드라인]
    1. 심층 요약 (Deep Summary): 
       - 뉴스 내용을 10~15문장 내외의 충분한 분량으로 아주 상세히 요약하세요.
       - 기사의 배경, 주요 인물/기업의 움직임, 핵심 수치/데이터, 원인과 결과, 향후 전망을 모두 포함해야 합니다.
       - 전문적인 경제 용어를 적절히 사용하여 깊이 있게 작성하세요.

    2. 전략적 시사점 (Strategic Insights): 
       - 패밀리 오피스의 자산 배분(Asset Allocation), 리스크 관리, 가업 승계, 혹은 운영 모델 측면에서의 시사점 2-3가지를 제시하세요.
       - 금융사나 컨설팅 펌의 관점이 패밀리 오피스 운영에 어떤 실질적인 영향을 줄지 분석하세요.

    언어: 한국어
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # 고품질 긴 문장 생성을 위해 GPT-4o 권장
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5 # 일관성 있는 분석을 위해 온도를 약간 낮춤
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류가 발생했습니다: {str(e)}"

# 4. 메인 실행 로직
if st.button('🚀 글로벌 뱅킹 & 컨설팅 동향 분석 시작'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner('글로벌 금융 네트워크 및 전략 컨설팅 데이터를 분석 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("조건에 맞는 최신 뉴스가 없습니다. 키워드를 넓혀 일반 검색을 수행합니다.")
                # 필터 없이 일반 검색 시도
                news_items = get_news("family office")
            
            for item in news_items:
                with st.expander(f"📑 {item.title}", expanded=True):
                    # 전체 화면을 넓게 쓰기 위해 컬럼 비중 조절
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.markdown(f"**Source Info**")
                        st.write(f"[Original Article]({item.link})")
                        published = getattr(item, 'published', '날짜 정보 없음')
                        st.caption(f"발행일: {published}")
                        st.divider()
                        st.info("🔍 **IB & Consulting Trend**")
                    
                    with col2:
                        analysis = analyze_article(item.title, item.link)
                        st.markdown(analysis)
                    
                    st.divider()
else:
    st.info("버튼을 누르면 주요 글로벌 금융사(IB/PB) 및 컨설팅 펌의 최신 패밀리 오피스 분석 자료를 가져옵니다.")
