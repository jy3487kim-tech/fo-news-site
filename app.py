import streamlit as st
import feedparser
from datetime import datetime
import openai

# 페이지 설정
st.set_page_config(page_title="Family Office Intelligence", page_icon="🏢", layout="wide")

# 사이드바 - 설정
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    news_count = st.slider("가져올 뉴스 개수", 3, 10, 5)
    st.info("이 사이트는 매일 최신 패밀리 오피스 관련 뉴스를 분석합니다.")

# 메인 화면 타이틀
st.title("🏢 Family Office Daily News & Insights")
st.subheader("오늘의 주요 뉴스, 요약 및 전략적 시사점")
st.divider()

# 뉴스 크롤링 함수
def get_news(keyword):
    # 구글 뉴스 RSS (한국어/글로벌 혼합 검색)
    rss_url = f"https://news.google.com/rss/search?q={keyword}+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    return feed.entries[:news_count]

# AI 분석 함수
def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 AI 요약과 시사점이 표시됩니다.", "N/A"
    
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
    당신은 글로벌 패밀리 오피스 전략 컨설턴트입니다. 다음 뉴스를 보고 보고서를 작성하세요.
    뉴스 제목: {title}
    
    형식:
    1. 요약: (뉴스 내용을 핵심 위주로 한 문장 요약)
    2. 시사점: (이 뉴스가 패밀리 오피스의 자산 배분, 가업 승계, 혹은 규제 대응에 주는 구체적인 시사점 2가지)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 실행 버튼
if st.button('✨ 최신 뉴스 분석 시작'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
    else:
        with st.spinner('글로벌 뉴스를 읽고 AI가 분석 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("오늘 생성된 새로운 뉴스가 없습니다.")
            
            for item in news_items:
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"### [{item.title}]({item.link})")
                        st.caption(f"발행일: {item.published}")
                    
                    with col2:
                        analysis = analyze_article(item.title, item.link)
                        st.markdown(analysis)
                    
                    st.divider()
else:
    st.write("버튼을 누르면 분석을 시작합니다.")
