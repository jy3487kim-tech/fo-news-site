import streamlit as st
import feedparser
from datetime import datetime, timedelta
import openai
from urllib.parse import quote
import time
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from io import BytesIO
import docx

# 1. 페이지 설정
st.set_page_config(page_title="Samsung Securities FO Strategy", page_icon="💙", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ Strategy Settings")
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ API Key 로드 완료")
    else:
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    
    news_count = st.slider("최대 분석 뉴스 개수", 1, 10, 3)

# --- 워드 파일 하이퍼링크 헬퍼 함수 ---
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

# --- 워드 리포트 생성 함수 ---
def create_word_report(report_items):
    doc = Document()
    doc.add_heading('Samsung Securities Family Office Strategic Intel Report', 0)
    doc.add_paragraph(f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("-" * 80)

    for item in report_items:
        doc.add_heading(f"{item['title']} ({item['source']}, {item['date']})", level=1)
        p = doc.add_paragraph("Original Article: ")
        add_hyperlink(p, item['link'], "Click here to read the full article")
        doc.add_heading('Strategic Analysis', level=2)
        doc.add_paragraph(item['analysis'])
        doc.add_page_break()
    
    target_stream = BytesIO()
    doc.save(target_stream)
    target_stream.seek(0)
    return target_stream

# 2. 뉴스 크롤링 함수
def get_news(keyword):
    sources_list = ["JPMorgan", "Goldman Sachs", "UBS", "Morgan Stanley", "Bloomberg", "Reuters", "Financial Times", "Forbes", "WSJ", "Blackstone", "KKR", "BlackRock", "Julius Baer", "Pictet", "Lombard Odier"]
    full_query = f'("{keyword}") AND ({" OR ".join([f'"{s}"' for s in sources_list])})'
    
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

# 3. 삼성증권 패밀리오피스 특화 AI 분석 함수
def analyze_article(title, link):
    if not api_key: return "API Key Error"
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    당신은 삼성증권 패밀리오피스(Samsung Securities Family Office) 전략팀의 수석 컨설턴트입니다. 
    다음 글로벌 뉴스를 바탕으로 삼성증권 패밀리오피스 비즈니스를 위한 심층 리포트를 작성하세요.

    뉴스 제목: {title}

    [보고서 작성 지침]
    1. 요약: 
       - 이 뉴스의 배경, 글로벌 금융사의 전략적 의도, 핵심 데이터, 시장의 반응 및 향후 전망을 포함하여 **반드시 20문장 이상의 풍부한 분량**으로 상세히 요약하세요. 
       - 단순 나열이 아닌, 인과관계가 명확한 전문적인 리포트 문장을 사용하세요.

    2. 전략 아이디어: 
       - 오직 '삼성증권 패밀리오피스' 비즈니스 관점에서만 서술하세요.
       ① [전략]: 삼성증권 패밀리오피스가 즉각 실행하거나 장기적으로 도입해야 할 구체적인 비즈니스 솔루션.
       ② [선정이유 및 전략적 타당성]: 글로벌 트렌드가 국내 초고액자산가 시장에 주는 영향과 삼성증권 패밀리오피스만의 강점을 결합한 분석.
       ③ [기대 효과 및 향후 과제]: 비즈니스 성과 예측 및 실행을 위한 패밀리오피스 전략팀의 구체적인 로드맵.
    
    언어: 한국어 (매우 격식 있고 전문적인 비즈니스 톤)
    """
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.5)
    return response.choices[0].message.content

# 4. 메인 UI 및 로직
st.title("🏛️ Samsung Securities Family Office Intel")
st.write("글로벌 최신 뉴스 기반 삼성증권 패밀리오피스 심층 전략 리포트")

if st.button('🚀 분석 및 리포트 생성'):
    if not api_key:
        st.error("OpenAI API Key를 설정해 주세요.")
    else:
        with st.spinner('글로벌 데이터를 분석하여 삼성증권 패밀리오피스 전용 리포트를 작성 중...'):
            news_items = get_news("family office")
            if not news_items:
                st.warning("최근 7일 이내 뉴스가 없습니다.")
            else:
                all_reports = []
                for item in news_items:
                    source_name = getattr(item, 'source', {}).get('title', 'Global Source')
                    try:
                        dt = datetime(*(item.published_parsed[:6]))
                        formatted_date = dt.strftime('%Y-%m-%d')
                    except: formatted_date = "N/A"
                        
                    analysis_result = analyze_article(item.title, item.link)
                    
                    with st.container():
                        st.markdown(f"## {item.title} ({source_name}, {formatted_date})")
                        st.write(f"🔗 [기사 원문 링크]({item.link})")
                        st.markdown(analysis_result)
                        st.divider()
                    
                    all_reports.append({
                        'title': item.title,
                        'source': source_name,
                        'link': item.link,
                        'date': formatted_date,
                        'analysis': analysis_result
                    })
                    time.sleep(1)

                docx_file = create_word_report(all_reports)
                st.download_button(
                    label="📂 워드 파일(.docx) 다운로드",
                    data=docx_file,
                    file_name=f"Samsung_FO_Strategy_{datetime.now().strftime('%Y%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
