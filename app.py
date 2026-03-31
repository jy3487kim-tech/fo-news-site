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
    
    # 1. 먼저 Secrets에서 키를 찾습니다.
    # 2. 만약 Secrets에 없다면(로컬 테스트용) 입력창을 보여줍니다.
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ API Key가 설정에서 로드되었습니다.")
    else:
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
        st.warning("⚠️ 자동 로그인을 위해 Streamlit Cloud의 Secrets 설정을 권장합니다.")
        
    news_count = st.slider("최대 분석 뉴스 개수", 1, 10, 5)
    st.info("글로벌 최신 뉴스를 기반으로 삼성증권 SNI 전략을 도출합니다.")

st.title("💙 Samsung Securities Family Office Strategic Intelligence")
st.subheader("최신 글로벌 금융 뉴스 기반 삼성증권 SNI 심층 전략 리포트")
st.divider()

# 2. 뉴스 크롤링 함수 (확장된 범위 및 Fallback 로직)
def get_news(keyword):
    # Tier 1: 주요 금융사 + 주요 경제 언론사 조합 (가장 선호하는 소스)
    sources = [
        "JPMorgan", "Goldman Sachs", "UBS", "Morgan Stanley", "Bloomberg", 
        "Reuters", "Financial Times", "Forbes", "WSJ", "CNBC", "Barron's",
        "Blackstone", "KKR", "BlackRock", "Julius Baer", "McKinsey", "Deloitte"
    ]
    
    entities_query = " OR ".join([f'"{s}"' for s in sources])
    # 전략적 검색 쿼리
    full_query = f'("{keyword}") AND ({entities_query})'
    
    def fetch_from_google(query):
        encoded_query = quote(query)
        # 최근 7일(when:7d)로 한정
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        filtered = []
        now = datetime.now()
        for entry in feed.entries:
            try:
                # 기사 날짜 확인 (최근 7일 이내인지 엄격 검증)
                pub_date = datetime(*(entry.published_parsed[:6]))
                if now - pub_date <= timedelta(days=7):
                    filtered.append(entry)
            except:
                filtered.append(entry) # 날짜 파싱 실패 시 포함
        return filtered

    # 1차 시도: 금융사/언론사 필터링 검색
    results = fetch_from_google(full_query)
    
    # 2차 시도: 만약 결과가 없다면 "family office" 키워드로만 검색 (Fallback)
    if not results:
        results = fetch_from_google(f'"{keyword}"')
        
    return results[:news_count]

# 3. 삼성증권 특화 심층 AI 분석 함수
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 전문 전략 리포트가 생성됩니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 삼성증권(Samsung Securities) 전략기획실 및 SNI(Samsung Private Banking) 본부의 수석 전략 컨설턴트입니다. 
    다음 글로벌 뉴스를 바탕으로 삼성증권 경영진에게 보고할 '심층 전략 분석서'를 작성하세요.

    뉴스 제목: {title}

    [보고서 작성 지침]

    1. 초정밀 심층 요약 (Hyper-Detailed Summary):
       - 이 뉴스의 핵심 내용과 배경을 30문장 내외로 매우 상세하게 서술하세요.
       - 단순히 기사 내용을 나열하는 것이 아니라, 해당 이슈의 금융사/언론사의 관점, 시장의 구조적 변화, 핵심 수치와 데이터를 다각도로 분석하여 리포트 형식으로 작성하세요.
       - 글로벌 자산관리 시장의 거시적 흐름(Macro Trend) 속에서 이 기사가 가지는 함의를 설명하세요.

    2. 삼성증권 패밀리오피스 전략적 시사점 및 실행 방안 (3 Strategic Insights):
       - 이 뉴스를 삼성증권 SNI 사업에 접목할 수 있는 구체적인 전략 3가지를 도출하세요.
       - 각 전략별로 '제안 내용'과 '선정이유 및 기대효과(Reasoning)'를 상세히 설명하세요.
       - 한국 시장의 특수성(상속세, 가업 승계 이슈 등)과 삼성증권의 강점(국내 최대 WM 인프라, IB 연계 역량)을 고려하여 실질적인 로드맵과 연결하세요.

    언어: 한국어 (전문적이고 격식 있는 비즈니스 문체)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류 발생: {str(e)}"

# 4. 실행 로직
if st.button('🚀 삼성증권 심층 전략 리포트 생성'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner('최근 7일간의 글로벌 뉴스를 정밀 분석 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("최근 7일 이내에 발행된 관련 뉴스를 찾을 수 없습니다. 잠시 후 다시 시도해 주세요.")
            
            for item in news_items:
                with st.container():
                    st.markdown(f"## 📘 [Strategy Report] {item.title}")
                    
                    # 메타 정보
                    published = getattr(item, 'published', '날짜 미상')
                    st.caption(f"📅 뉴스 발행일: {published} | 🔗 [Original Article]({item.link})")
                    
                    # AI 분석 결과
                    analysis = analyze_article(item.title, item.link)
                    st.markdown(analysis)
                    
                    st.divider()
                    time.sleep(1)
else:
    st.info("버튼을 누르면 삼성증권 SNI 비즈니스 고도화를 위한 글로벌 전략 리포트 생성을 시작합니다.")
