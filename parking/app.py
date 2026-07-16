import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

#######################################
# 페이지 설정
#######################################

st.set_page_config(
    page_title="🚗 서울 공영주차장 찾기",
    page_icon="🚗",
    layout="wide"
)

#######################################
# CSS
#######################################

st.markdown("""
<style>

.stApp{
background:#FFF4FB;
}

h1{
color:#ff5fa2;
text-align:center;
}

.block-container{
padding-top:2rem;
}

div[data-testid="stMetric"]{
background:white;
padding:15px;
border-radius:20px;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
}

.stButton>button{
background:#ff7eb6;
color:white;
border:none;
border-radius:20px;
font-size:18px;
}

.stButton>button:hover{
background:#ff4f9b;
}

</style>
""", unsafe_allow_html=True)

#######################################
# 제목
#######################################

st.title("🚗💕 서울 공영주차장 찾기")

st.write("핑크 감성 주차장 검색 서비스")

#######################################
# 업로드
#######################################

uploaded = st.file_uploader(
    "CSV 업로드",
    type="csv"
)

if uploaded:

    try:
        df = pd.read_csv(uploaded, encoding="cp949")
    except:
        df = pd.read_csv(uploaded)

else:

    try:
        df = pd.read_csv(
            "서울시 공영주차장 안내 정보 (2).csv",
            encoding="cp949"
        )
    except:
        st.stop()

#######################################
# 컬럼 이름
#######################################

addr_col = "주소"
name_col = "주차장명"

lat_col = "위도"
lon_col = "경도"

#######################################
# 좌표 없는 데이터 제거
#######################################

df = df.dropna(subset=[lat_col, lon_col])

#######################################
# 자치구 추출
#######################################

df["자치구"] = df[addr_col].str.extract(r"(강남구|강동구|강북구|강서구|관악구|광진구|구로구|금천구|노원구|도봉구|동대문구|동작구|마포구|서대문구|서초구|성동구|성북구|송파구|양천구|영등포구|용산구|은평구|종로구|중구|중랑구)")

#######################################
# 사이드바
#######################################

st.sidebar.header("검색")

district = st.sidebar.selectbox(
    "자치구",
    ["전체"] + sorted(df["자치구"].dropna().unique())
)

keyword = st.sidebar.text_input("주차장 검색")

#######################################
# 요금 컬럼
#######################################

fee_col = "기본 주차 요금"

if fee_col in df.columns:

    df[fee_col] = (
        df[fee_col]
        .astype(str)
        .str.replace(",","")
        .str.extract("([0-9]+)")
        .fillna(0)
        .astype(int)
    )

    max_fee = int(df[fee_col].max())

    price = st.sidebar.slider(
        "최대 기본요금",
        0,
        max_fee,
        max_fee
    )

    df = df[df[fee_col] <= price]

#######################################
# 필터
#######################################

if district!="전체":
    df=df[df["자치구"]==district]

if keyword:
    df=df[df[name_col].str.contains(keyword)]

#######################################
# 통계
#######################################

c1,c2,c3=st.columns(3)

c1.metric("주차장",len(df))

if fee_col in df.columns:
    c2.metric("평균 기본요금",f"{int(df[fee_col].mean())}원")

free=0

if "무료 개방 여부" in df.columns:
    free=(df["무료 개방 여부"]=="Y").sum()

c3.metric("무료 주차장",free)

#######################################
# 지도
#######################################

m=folium.Map(
    location=[37.55,126.98],
    zoom_start=11
)

for _,row in df.iterrows():

    popup=f"""
    <b>🚗 {row[name_col]}</b><br>

    📍 {row[addr_col]}<br>

    💰 기본요금 :
    {row.get("기본 주차 요금","-")}원<br>

    🆓 무료 :
    {row.get("무료 개방 여부","-")}<br>

    📅 주말 :
    {row.get("토요일 유무료구분","-")}<br>

    ⏰ 운영시간 :
    {row.get("평일 운영 시작시각","-")}~
    {row.get("평일 운영 종료시각","-")}
    """

    folium.Marker(
        [row[lat_col],row[lon_col]],
        popup=popup,
        tooltip="🚗",
        icon=folium.Icon(
            color="pink",
            icon="car",
            prefix="fa"
        )
    ).add_to(m)

st_folium(
    m,
    width=1200,
    height=650
)

#######################################
# 가장 싼 곳
#######################################

if fee_col in df.columns and len(df)>0:

    cheapest=df.sort_values(fee_col).iloc[0]

    st.success(
f"""
💕 가장 저렴한 주차장

🚗 {cheapest[name_col]}

📍 {cheapest[addr_col]}

💰 {cheapest[fee_col]}원
"""
)

#######################################
# 표
#######################################

st.dataframe(df,use_container_width=True)

#######################################
# 다운로드
#######################################

csv=df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 결과 다운로드",
    csv,
    "parking.csv",
    "text/csv"
)
