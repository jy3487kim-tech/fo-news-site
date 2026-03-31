import streamlit as st
import feedparser
from datetime import datetime, timedelta
import openai
from urllib.parse import quote
import time
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(page_title="Samsung Securities FO Strategy", page_icon="💙", layout="wide")

# 사이드바 설정 (Secrets 로드)
with st.sidebar:
    st.title("⚙️ Strategy Settings")
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ API Key 로드 완료")
    else:
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    
    news_count = st.slider("최대 분석 뉴스 개수", 1, 10, 3)

# --- 워드 파일 하이퍼링크 삽입을 위한 헬퍼 함수 ---
def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')
    c = docx.oxml.shared.OxmlElement('w:rStyle')
    c.set(docx.oxml.shared.qn('w:val'), 'Hyperlink')
    rPr.append(c)
    new_run.append(rPr)
    text_obj = docx.oxml.shared.OxmlElement('w:t')
    text_obj.text = text
    new_run.append(text_obj)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink

import docx # 헬퍼 함수에서 사용하기 위해 임포트

# --- 분석 리포트 생성 함수 ---
def create_word_report(report_items):
    doc = Document()
    doc.add_heading('Samsung Securities FO Strategic Intelligence Report', 0)
    doc.add_paragraph(f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("-" * 50)

    for item in report_items:
        doc.add_heading(item['title'], level=1)
        
        # 하이퍼링크 추가
        p = doc.add_paragraph("Original Article: ")
        add_hyperlink(p, item['link'], "Click here to read the full article")
        
        doc.add_paragraph(f"Published Date: {item['date']}")
        
        doc.add_heading('Strategic Analysis', level=2)
        doc.add_paragraph(item['analysis'])
        doc.add_page_break()
    
    target_stream = BytesIO()
    doc.save(target_stream)
    target_stream.seek(0)
    return target_stream

# 2. 뉴스 크롤링 함수
def get_news(keyword):
    sources = ["JPMorgan", "Goldman Sachs", "UBS", "Morgan Stanley", "Bloomberg", "Reuters", "Financial Times", "Forbes", "WSJ", "Blackstone", "KKR", "BlackRock"]
    full_query = f'("{keyword}") AND ({" OR ".join([f'"{s}"' for s in sources])})'
    
    def fetch(query):
        encoded = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded}+when:7d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        now = datetime.now()
        filtered = []
        for entry in feed.entries:
            try:
                p_date = datetime(*(entry.published_parsed[:6]))
                if now - p_date <= timedelta(days=7):
                    filtered.append(entry)
            except: filtered.append(entry)
        return filtered

    res = fetch(full_query)
    if not res: res = fetch(f'"{keyword}"')
    return res[:news_count]

# 3. AI 분석 함수 (단일 전략 강화형)
def analyze_article(title, link):
    if not api_key: return "API Key Error"
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
    당신은 삼성증권 전략기획실 수석 컨설턴트입니다. 다음 뉴스를 바탕으로 '단일 핵심 전략 분석서'를 작성하세요.
    뉴스 제목: {title}
    1. 초정밀 심층 요약: 30문장 내외로 상세히 요약. 글로벌 시장 맥락 포함.
    2. 삼성증권 패밀리오피스 단일 핵심 전략: 
       ① [제안 내용] ② [선정 이유 및 전략적 타당성] ③ [기대 효과 및 향후 과제]
    언어: 한국어 (전문 비즈니스 문체)
    """
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.4)
    return response.choices[0].message.content

# 4. 메인 UI 및 로직
st.title("🏛️ Samsung Securities FO Strategic Intel")
st.write("글로벌 최신 뉴스 기반 삼성증권 SNI 심층 전략 리포트")

if st.button('🚀 분석 및 리포트 생성'):
    if not api_key:
        st.error("OpenAI API Key를 설정해 주세요.")
    else:
        with st.spinner('데이터 분석 및 워드 파일 생성 중...'):
            news_items = get_news("family office")
            if not news_items:
                st.warning("최근 7일 이내 뉴스가 없습니다.")
            else:
                all_reports = []
                for item in news_items:
                    analysis_result = analyze_article(item.title, item.link)
                    
                    # 화면 표시
                    with st.container():
                        st.markdown(f"### 📑 {item.title}")
                        st.write(f"[Original Link]({item.link})")
                        st.markdown(analysis_result)
                        st.divider()
                    
                    # 데이터 저장 (워드 생성용)
                    all_reports.append({
                        'title': item.title,
                        'link': item.link,
                        'date': getattr(item, 'published', 'N/A'),
                        'analysis': analysis_result
                    })
                    time.sleep(1)

                # 워드 파일 생성
                docx_file = create_word_report(all_reports)
                
                # 다운로드 버튼 표시
                st.download_button(
                    label="📂 워드 파일(.docx) 다운로드",
                    data=docx_file,
                    file_name=f"Samsung_FO_Strategy_{datetime.now().strftime('%Y%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
