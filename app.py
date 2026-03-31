import streamlit as st
import feedparser
from datetime import datetime, timedelta
import openai
from urllib.parse import quote
import time

# 1. 페이지 설정
st.set_page_config(page_title="Samsung Securities FO Strategy", page_icon="💙", layout="wide")

# 사이드바 설정 (Secrets 로드 로직 포함)
with st.sidebar:
    st.title("⚙️ Strategy Settings")
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ API Key가 설정에서 로드되었습니다.")
    else:
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    
    news_count = st.slider("최대 분석 뉴스 개수", 1, 10, 3)
    st.info("글로벌 금융 데이터를 기반으로 삼성증권 SNI의 단일 핵심 전략을 도출합니다.")

st.title("💙 Samsung Securities Family Office Strategic Intelligence")
st.subheader("글로벌 금융 트렌드 기반 삼성증권 SNI 단일 핵심 전략 리포트")
st.divider()

# 2. 뉴스 크롤링 함수 (금융사 + 언론사 + Fallback)
def get_news(keyword):
    sources = [
        "JPMorgan", "Goldman Sachs", "UBS", "Morgan Stanley", "Bloomberg", 
        "Reuters", "Financial Times", "Forbes", "WSJ", "CNBC", "Barron's",
        "Blackstone", "KKR", "BlackRock", "Julius Baer", "McKinsey", "Deloitte"
    ]
    
    entities_query = " OR ".join([f'"{s}"' for s in sources])
    full_query = f'("{keyword}") AND ({entities_query})'
    
    def fetch_from_google(query):
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:7d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        filtered = []
        now = datetime.now()
        for entry in feed.entries:
            try:
                pub_date = datetime(*(entry.published_parsed[:6]))
                if now - pub_date <= timedelta(days=7):
                    filtered.append(entry)
            except:
                filtered.append(entry)
        return filtered

    results = fetch_from_google(full_query)
    if not results:
        results = fetch_from_google(f'"{keyword}"')
    return results[:news_count]

# 3. 삼성증권 특화 심층 AI 분석 함수 (단일 전략 강화형)
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key가 필요합니다."
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 삼성증권(Samsung Securities) 전략기획실 및 SNI(Samsung Private Banking) 본부의 수석 전략 컨설턴트입니다. 
    다음 글로벌 뉴스를 바탕으로 삼성증권 경영진에게 보고할 '단일 핵심 전략 분석서'를 작성하세요.

    뉴스 제목: {title}

    [보고서 작성 가이드라인]

    1. 초정밀 심층 요약 (Hyper-Detailed Summary):
       - 이 뉴스의 핵심 내용과 배경을 30문장 내외로 매우 상세하게 서술하세요.
       - 글로벌 자산관리 시장의 거시적 흐름과 해당 이슈의 상관관계를 심층 분석하여 리포트 형식으로 작성하세요.

    2. 삼성증권 패밀리오피스 단일 핵심 전략 (One Core Strategic Insight):
       - 이 뉴스에서 도출할 수 있는 가장 가치 있는 '단 하나의 핵심 전략'을 제시하세요.
       - 아래 세 가지 항목을 포함하여 아주 상세하게 기술해야 합니다:
         ① [제안 내용]: 삼성증권 SNI가 즉각적 혹은 장기적으로 실행해야 할 구체적인 비즈니스 모델, 상품 기획, 혹은 서비스 혁신 방안.
         ② [선정 이유 및 전략적 타당성 (Reasoning)]: 왜 이 전략이 지금 삼성증권에 필요한지 글로벌 IB의 사례와 한국 UHNWI 시장(상속, 가업승계, 대체투자 수요 등)의 특수성을 결합하여 심층 설명하세요.
         ③ [기대 효과 및 향후 과제 (Impact & Roadmap): 이 전략을 통해 달성할 수 있는 정량적/정성적 성과와 실행을 위해 해결해야 할 선결 과제를 제시하세요.

    언어: 한국어 (전문적이고 비즈니스적인 톤 유지)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4 # 정밀한 분석을 위해 낮은 온도 설정
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 분석 중 오류 발생: {str(e)}"

# 4. 메인 실행 로직
if st.button('🚀 삼성증권 단일 핵심 전략 리포트 생성'):
    if not api_key:
        st.error("OpenAI API Key를 설정해 주세요.")
    else:
        with st.spinner('글로벌 데이터를 정밀 분석하여 삼성증권 전용 전략을 도출 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("최근 7일 이내의 관련 뉴스가 없습니다.")
            
            for item in news_items:
                with st.container():
                    st.markdown(f"## 🏛️ [Strategic Report] {item.title}")
                    
                    # 메타 정보
                    published = getattr(item, 'published', '날짜 미상')
                    st.caption(f"📅 뉴스 발행일: {published} | 🔗 원문 주소: [기사 보기]({item.link})")
                    
                    # AI 분석 결과
                    analysis = analyze_article(item.title, item.link)
                    st.markdown(analysis)
                    
                    st.divider()
                    time.sleep(1)
else:
    st.info("버튼을 누르면 삼성증권 SNI 고도화를 위한 단 하나의 핵심 전략 리포트를 생성합니다.")
