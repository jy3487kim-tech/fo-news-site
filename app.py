import streamlit as st
import feedparser
from datetime import datetime, timedelta
import openai
from urllib.parse import quote
import time

# 1. 페이지 설정 및 삼성증권 테마 적용
st.set_page_config(page_title="Samsung Securities FO Strategy Intel", page_icon="💙", layout="wide")

with st.sidebar:
    st.title("⚙️ Strategy Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    news_count = st.slider("최대 분석 뉴스 개수", 1, 10, 5)
    st.info("""
    **분석 타겟:**
    - 글로벌 Top-tier IB 및 컨설팅 펌 리포트
    - 삼성증권 SNI 서비스 고도화 전략 도출
    - 국내 1위를 넘어 글로벌 경쟁력 확보
    """)

st.title("💙 Samsung Securities Family Office Strategic Intelligence")
st.subheader("삼성증권 패밀리오피스 고도화를 위한 글로벌 금융 동향 심층 분석")
st.divider()

# 2. 뉴스 크롤링 및 엄격한 7일 필터링 함수
def get_news(keyword):
    entities = [
        "JPMorgan", "Goldman Sachs", "UBS", "Julius Baer", "Morgan Stanley",
        "McKinsey", "BCG", "Deloitte", "Blackstone", "KKR", "BlackRock",
        "Pictet", "Lombard Odier", "HSBC Private Banking", "Bain & Company"
    ]
    
    entities_query = " OR ".join([f'"{e}"' for e in entities])
    full_query = f'({keyword}) AND ({entities_query})'
    encoded_query = quote(full_query)
    
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    filtered_entries = []
    now = datetime.now()
    
    for entry in feed.entries:
        try:
            published_time = datetime(*(entry.published_parsed[:6]))
            if now - published_time <= timedelta(days=7):
                filtered_entries.append(entry)
        except:
            filtered_entries.append(entry)
            
    return filtered_entries[:news_count]

# 3. 삼성증권 특화 심층 AI 분석 함수
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 전문 전략 리포트가 생성됩니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 삼성증권(Samsung Securities) 전략기획실 및 SNI(Samsung Nuclear Insignia) 본부의 수석 전략 컨설턴트입니다. 
    다음 글로벌 뉴스를 바탕으로 삼성증권 경영진에게 보고할 '심층 전략 분석서'를 작성하세요.

    뉴스 제목: {title}

    [보고서 작성 필수 항목]

    1. 초정밀 심층 요약 (Hyper-Detailed Summary):
       - 이 뉴스의 핵심 내용과 배경을 30문장 내외로 매우 상세하게 서출하세요.
       - 단순히 기사 내용을 나열하는 것이 아니라, 해당 금융사/컨설팅펌이 왜 이런 움직임을 보이는지, 시장의 구조적 변화와 어떤 관련이 있는지, 공개된 수치나 데이터가 있다면 이를 바탕으로 다각도에서 분석하세요.
       - 글로벌 자산관리 시장의 거시적 흐름(Macro Trend) 속에서 이 뉴스가 가지는 위치를 설명하세요.

    2. 삼성증권 패밀리오피스전략적 시사점 및 실행 방안 (3 Strategic Insights for Samsung Securities):
       - 이 뉴스를 삼성증권 SNI 사업에 접목할 수 있는 구체적인 전략 3가지를 도출하세요.
       - 각 전략별로 '제안 내용'과 '선정이유 및 기대효과(Reasoning)'를 상세히 설명하세요.
       - 한국 시장의 특수성(상속세, 기업 승계 이슈 등)과 삼성증권의 강점(IB 연계, 국내 최대 자산관리 인프라)을 고려하여 실질적이고 장기적인 로드맵과 연결하세요.

    언어: 한국어 (전문적이고 격식 있는 비즈니스 문체 사용)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5 # 일관성과 전문성 유지를 위해 설정
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류 발생: {str(e)}"

# 4. 메인 실행 로직
if st.button('🚀 삼성증권 심층 전략 리포트 생성'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner('최근 7일간의 글로벌 데이터를 정밀 분석하여 삼성증권 전용 리포트를 작성 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("최근 7일 이내의 조건에 맞는 글로벌 뉴스가 없습니다. 키워드를 조정해 보세요.")
            
            for item in news_items:
                with st.container():
                    st.markdown(f"## 📘 [Strategy Report] {item.title}")
                    
                    # 메타 정보
                    published = getattr(item, 'published', '날짜 미상')
                    st.caption(f"📅 분석 기준일: {published} | 🔗 원문 주소: [기사 보기]({item.link})")
                    
                    # 분석 결과 출력
                    analysis = analyze_article(item.title, item.link)
                    
                    # 가독성을 위해 요약 부분과 전략 부분을 시각적으로 구분하여 출력할 수 있도록 AI 응답을 활용
                    st.markdown(analysis)
                    
                    st.divider()
                    time.sleep(1.5) # API 안정성 확보
else:
    st.info("버튼을 누르면 삼성증권 SNI 비즈니스 고도화를 위한 글로벌 심층 전략 보고서가 생성됩니다.")
