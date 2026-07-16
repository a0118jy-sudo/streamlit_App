import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 도서관 지도",
    page_icon="📚",
    layout="wide"
)

st.title("📚 서울시 도서관 정보")

uploaded = st.file_uploader(
    "도서관 CSV 업로드",
    type="csv"
)

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded, encoding="cp949")
    except:
        df = pd.read_csv(uploaded)

else:
    st.info("CSV 파일을 업로드해주세요.")
    st.stop()

###########################################
# 컬럼명
###########################################

NAME = "도서관명"
DISTRICT = "구명"
ADDRESS = "주소"
PHONE = "전화번호"
HOLIDAY = "정기 휴관일"
LAT = "위도"
LON = "경도"

###########################################
# 좌표 없는 데이터 제거
###########################################

df = df.dropna(subset=[LAT, LON])

###########################################
# 자치구 선택
###########################################

district_list = ["전체"] + sorted(df[DISTRICT].dropna().unique())

district = st.sidebar.selectbox(
    "자치구 선택",
    district_list
)

if district != "전체":
    filtered = df[df[DISTRICT] == district]
else:
    filtered = df.copy()

###########################################
# 통계
###########################################

c1, c2 = st.columns(2)

c1.metric(
    "전체 도서관",
    len(df)
)

c2.metric(
    "선택된 도서관",
    len(filtered)
)

###########################################
# 지도
###########################################

center_lat = filtered[LAT].mean()
center_lon = filtered[LON].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11
)

cluster = MarkerCluster().add_to(m)

for _, row in filtered.iterrows():

    popup = f"""
    <b>{row[NAME]}</b><br><br>

    📍 주소<br>
    {row[ADDRESS]}<br><br>

    ☎ 전화번호<br>
    {row[PHONE]}<br><br>

    🚫 휴관일<br>
    {row[HOLIDAY]}
    """

    folium.Marker(
        location=[row[LAT], row[LON]],
        tooltip=row[NAME],
        popup=popup,
        icon=folium.Icon(
            color="blue",
            icon="book",
            prefix="fa"
        )
    ).add_to(cluster)

st_folium(
    m,
    width=1200,
    height=650
)

###########################################
# 도서관 목록
###########################################

st.subheader("📚 도서관 목록")

show = filtered[
    [
        NAME,
        DISTRICT,
        ADDRESS,
        PHONE,
        HOLIDAY
    ]
].reset_index(drop=True)

st.dataframe(
    show,
    use_container_width=True
)
