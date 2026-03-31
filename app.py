import streamlit as st
import feedparser
from datetime import datetime, timedelta
import openai
from urllib.parse import quote
import time

# 1. 페이지 설정
st.set_page_config(page_title="Samsung Securities FO Intel", page_icon="💙", layout="wide")

with st.sidebar:
    st.title("⚙️ Strategy Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    news_count = st.slider("최대 분석 뉴스 개수", 3, 15, 7)
    st.info("""
    **분석 목표:**
    - 글로벌 트렌드 기반 삼성증권 FO 전략 도출
    - SNI 서비스 고도화 및 장기 로드맵 인사이트
    """)

st.title("💙 Samsung Securities Family Office Strategic Intelligence")
st.subheader("글로벌 금융 동향 기반 삼성증권 패밀리오피스 전략 보고서")
st.divider()

# 2. 뉴스 크롤링 및 날짜 필터링 함수
def get_news(keyword):
    # 금융/컨설팅/사모펀드 검색 범위 확장
    entities = [
        "JPMorgan", "Goldman Sachs", "UBS", "Julius Baer", "Morgan Stanley",
        "McKinsey", "BCG", "Deloitte", "PwC", "Blackstone", "KKR", "BlackRock",
        "Pictet", "Lombard Odier", "HSBC Private Banking"
    ]
    
    entities_query = " OR ".join([f'"{e}"' for e in entities])
    full_query = f'({keyword}) AND ({entities_query})'
    encoded_query = quote(full_query)
    
    # 구글 뉴스 RSS (최근 7일 설정)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    # [업데이트] 파이썬 레벨에서 7일 이내 기사인지 한 번 더 검증
    filtered_entries = []
    now = datetime.now()
    
    for entry in feed.entries:
        # 발행일 파싱
        try:
            published_time = datetime(*(entry.published_parsed[:6]))
            if now - published_time <= timedelta(days=7):
                filtered_entries.append(entry)
        except:
            # 날짜 파싱 실패 시 혹시 모르니 포함
            filtered_entries.append(entry)
            
    return filtered_entries[:news_count]

# 3. 삼성증권 특화 AI 분석 함수
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 전략 보고서가 생성됩니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 삼성증권(Samsung Securities)의 패밀리오피스 및 초고액자산가(UHNWI) 사업 전략팀의 수석 컨설턴트입니다. 
    다음 뉴스를 분석하여 삼성증권 경영진에게 보고할 '전략 보고서'를 작성하세요.

    뉴스 제목: {title}

    [보고서 작성 가이드라인]
    1. 심층 요약 (Deep Summary): 
       - 뉴스 내용을 10~15문장으로 아주 상세히 요약하세요. 
       - 기사의 배경, 글로벌 IB/컨설팅 펌의 핵심 액션, 주요 수치 및 시장 전망을 구체적으로 포함하세요.

    2. 삼성증권 패밀리오피스 전략적 시사점 (Strategic Implications for Samsung Securities): 
       - 이 뉴스가 삼성증권의 패밀리오피스(SNI) 사업 경쟁력 강화에 어떤 의미가 있는지 분석하세요.
       - 글로벌 리딩 뱅크의 사례를 삼성증권의 국내외 자산관리 모델에 어떻게 이식할 수 있을지 제안하세요.

    3. 삼성증권 장기 전략과의 연결 (Alignment with Long-term Roadmap): 
       - 삼성증권이 국내 No.1 패밀리오피스를 넘어 글로벌 경쟁력을 갖추기 위해 이 사례를 장기 로드맵(예: 디지털 전환, 글로벌 대체투자 확대, 가업 승계 플랫폼 고도화 등)과 어떻게 연결해야 할지 구체적인 인사이트를 제시하세요.

    언어: 한국어
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류: {str(e)}"

# 4. 실행 섹션
if st.button('🚀 삼성증권 전용 전략 분석 실행'):
    if not api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner('최근 7일간의 글로벌 데이터를 필터링하고 삼성증권 전용 인사이트를 도출 중...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("최근 7일 이내의 조건에 맞는 뉴스가 없습니다. 검색 범위를 조금 넓혀보세요.")
            
            for item in news_items:
                # 카드 형태의 디자인
                with st.container():
                    st.markdown(f"### 📑 {item.title}")
                    
                    # 정보 요약 바
                    published = getattr(item, 'published', '날짜 정보 없음')
                    st.caption(f"🗓️ 발행일: {published} | 🔗 [Original Source]({item.link})")
                    
                    # 분석 결과
                    analysis = analyze_article(item.title, item.link)
                    st.markdown(analysis)
                    
                    st.divider()
                    time.sleep(1) # API 레이트 리밋 방지
else:
    st.info("버튼을 누르면 삼성증권 패밀리오피스 사업을 위한 글로벌 전략 리포트를 생성합니다.")
