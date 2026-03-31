import streamlit as st
import feedparser
from datetime import datetime
import openai
from urllib.parse import quote

st.set_page_config(page_title="Family Office Intelligence", page_icon="🏢", layout="wide")

with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    news_count = st.slider("가져올 뉴스 개수", 3, 15, 7) # 개수 범위를 조금 늘림
    st.info("이 앱은 최근 7일간의 글로벌 패밀리 오피스 뉴스를 분석합니다.")

st.title("🏢 Family Office Daily News & Insights")
st.subheader("글로벌 주요 뉴스, 요약 및 전략적 시사점")
st.divider()

def get_news(keyword):
    encoded_keyword = quote(keyword)
    # 최근 7일(7d), 글로벌 영어 뉴스 기준(US:en)으로 검색
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    return feed.entries[:news_count]

def analyze_article(title, link):
    if not api_key:
        return "⚠️ API Key를 입력하면 AI 분석이 표시됩니다.", "N/A"
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # 영문 뉴스를 읽고 한국어로 요약하도록 프롬프트 수정
        prompt = f"""
        당신은 글로벌 패밀리 오피스 전략 컨설턴트입니다. 
        다음 뉴스 제목(영어 또는 한국어)을 분석하여 한국어로 보고서를 작성하세요.
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
    except Exception as e:
        return f"❌ 분석 중 오류가 발생했습니다: {str(e)}"

if st.button('✨ 최신 뉴스 분석 시작'):
    if not api_key:
        st.error("오른쪽 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
    else:
        with st.spinner('글로벌 뉴스를 검색하고 AI가 분석 중입니다...'):
            news_items = get_news("family office")
            
            if not news_items:
                st.warning("최근 7일간 검색된 새로운 뉴스가 없습니다.")
            
            for item in news_items:
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"### [{item.title}]({item.link})")
                        published = getattr(item, 'published', '날짜 정보 없음')
                        st.caption(f"발행일: {published}")
                    with col2:
                        analysis = analyze_article(item.title, item.link)
                        st.markdown(analysis)
                    st.divider()
else:
    st.write("버튼을 누르면 최근 7일간의 글로벌 뉴스를 가져와 분석합니다.")
