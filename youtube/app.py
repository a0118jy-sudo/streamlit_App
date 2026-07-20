import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import requests
import re

from wordcloud import WordCloud
from googleapiclient.discovery import build
from collections import Counter
from datetime import datetime

from konlpy.tag import Okt

from utils import (
    get_video_id,
    get_comments,
    sentiment_analysis,
    make_wordcloud,
    draw_time_chart,
    top_keywords
)

##################################################
# 페이지 설정
##################################################

st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="📺",
    layout="wide"
)

##################################################
# CSS
##################################################

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

.stButton>button{
    width:100%;
}

</style>
""", unsafe_allow_html=True)

##################################################
# 제목
##################################################

st.title("📺 YouTube 댓글 분석기")

st.write(
"""
유튜브 영상을 분석하여

- 댓글 수집
- 시간대별 댓글 추이
- 감성분석
- 한글 워드클라우드

를 생성합니다.
"""
)

##################################################
# API KEY
##################################################

API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

##################################################
# Sidebar
##################################################

st.sidebar.header("분석 옵션")

comment_limit = st.sidebar.slider(
    "댓글 개수",
    100,
    5000,
    500,
    step=100
)

##################################################
# URL 입력
##################################################

url = st.text_input(
    "유튜브 URL",
    placeholder="https://www.youtube.com/watch?v=xxxxxxxx"
)

##################################################
# 분석 버튼
##################################################

analyze = st.button("댓글 분석 시작")

##################################################
# URL이 입력되면 영상 보여주기
##################################################

if url != "":

    video_id = get_video_id(url)

    if video_id:

        st.video(url)

##################################################
# 버튼 클릭
##################################################

if analyze:

    if url == "":

        st.warning("유튜브 URL을 입력하세요.")
        st.stop()

    video_id = get_video_id(url)

    if video_id is None:

        st.error("올바른 유튜브 URL이 아닙니다.")
        st.stop()

    ##################################################
    # 영상 정보
    ##################################################

    with st.spinner("영상 정보를 불러오는 중..."):

        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )

        response = request.execute()

    if len(response["items"]) == 0:

        st.error("영상을 찾을 수 없습니다.")
        st.stop()

    video = response["items"][0]

    snippet = video["snippet"]
    stats = video["statistics"]

    title = snippet["title"]
    channel = snippet["channelTitle"]
    published = snippet["publishedAt"]

    view = int(stats.get("viewCount",0))
    like = int(stats.get("likeCount",0))

    ##################################################
    # 영상 정보 출력
    ##################################################

    col1,col2 = st.columns([1,1])

    with col1:

        st.subheader(title)

        st.write("채널 :",channel)

        st.write("게시일 :",published[:10])

    with col2:

        st.metric("조회수",f"{view:,}")

        st.metric("좋아요",f"{like:,}")

    st.divider()

    ##################################################
    # 댓글 수집
    ##################################################

    progress = st.progress(0)

    status = st.empty()

    status.write("댓글 수집 중...")

    comments = get_comments(
        youtube=youtube,
        video_id=video_id,
        max_comments=comment_limit,
        progress=progress,
        status=status
    )

    progress.progress(100)

    status.success("댓글 수집 완료!")

    if len(comments)==0:

        st.error("댓글이 없습니다.")
        st.stop()

    ##################################################
    # DataFrame
    ##################################################

    df = pd.DataFrame(comments)

    df["published"] = pd.to_datetime(df["published"])

    st.success(f"{len(df):,}개의 댓글 수집 완료")

    st.dataframe(
        df.head(),
        use_container_width=True
    )
    ##################################################
    # 감성분석
    ##################################################

    st.header("😊 댓글 감성분석")

    with st.spinner("감성분석 중..."):

        df["sentiment"] = df["comment"].apply(
            sentiment_analysis
        )

    sentiment_count = (
        df["sentiment"]
        .value_counts()
        .reset_index()
    )

    sentiment_count.columns = [
        "감정",
        "개수"
    ]

    col1, col2 = st.columns([1, 2])

    with col1:

        st.dataframe(
            sentiment_count,
            use_container_width=True
        )

    with col2:

        fig = px.pie(
            sentiment_count,
            names="감정",
            values="개수",
            hole=0.45,
            color="감정",
            color_discrete_map={
                "긍정":"#00CC96",
                "부정":"#EF553B",
                "중립":"#636EFA"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    ##################################################
    # 시간대별 댓글 추이
    ##################################################

    st.header("📈 댓글 작성 추이")

    mode = st.radio(
        "분석 기준",
        [
            "일별",
            "월별",
            "시간별"
        ],
        horizontal=True
    )

    time_fig = draw_time_chart(
        df,
        mode
    )

    st.plotly_chart(
        time_fig,
        use_container_width=True
    )

    st.divider()

    ##################################################
    # 댓글 길이
    ##################################################

    st.header("📝 댓글 길이 분석")

    df["length"] = (
        df["comment"]
        .astype(str)
        .apply(len)
    )

    length_fig = px.histogram(
        df,
        x="length",
        nbins=40,
        title="댓글 길이 분포"
    )

    st.plotly_chart(
        length_fig,
        use_container_width=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "평균 길이",
            round(df["length"].mean(),1)
        )

    with col2:

        st.metric(
            "최대 길이",
            df["length"].max()
        )

    with col3:

        st.metric(
            "최소 길이",
            df["length"].min()
        )

    st.divider()

    ##################################################
    # Top20 키워드
    ##################################################

    st.header("🔥 많이 사용된 단어")

    keyword_df = top_keywords(df)

    if len(keyword_df) > 0:

        fig = px.bar(
            keyword_df,
            x="단어",
            y="빈도",
            text="빈도",
            color="빈도"
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="빈도"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            keyword_df,
            use_container_width=True
        )

    else:

        st.info("추출된 키워드가 없습니다.")

    st.divider()

    ##################################################
    # 댓글 다운로드
    ##################################################

    st.header("💾 댓글 다운로드")

    csv = (
        df
        .to_csv(index=False)
        .encode("utf-8-sig")
    )

    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name=f"{video_id}_comments.csv",
        mime="text/csv"
    )

    st.divider()
  
    st.divider()

    ##################################################
    # 워드클라우드
    ##################################################

    st.header("☁️ 한글 워드클라우드")

    with st.spinner("워드클라우드 생성 중..."):

        wc = make_wordcloud(df)

    if wc is not None:

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.imshow(
            wc,
            interpolation="bilinear"
        )

        ax.axis("off")

        st.pyplot(fig)

    else:

        st.warning("워드클라우드를 생성할 수 없습니다.")

    st.divider()

    ##################################################
    # 분석 요약
    ##################################################

    st.header("📋 분석 요약")

    positive = (
        df["sentiment"] == "긍정"
    ).sum()

    negative = (
        df["sentiment"] == "부정"
    ).sum()

    neutral = (
        df["sentiment"] == "중립"
    ).sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "긍정",
        f"{positive:,}"
    )

    c2.metric(
        "부정",
        f"{negative:,}"
    )

    c3.metric(
        "중립",
        f"{neutral:,}"
    )

    st.success("분석이 완료되었습니다.")

##################################################
# 예외 처리
##################################################

try:
    pass

except Exception as e:

    st.error("오류가 발생했습니다.")

    st.exception(e)
