import re
import os
import requests
import pandas as pd

from datetime import datetime

from konlpy.tag import Okt

from wordcloud import WordCloud

import matplotlib.pyplot as plt
import plotly.express as px


##################################################
# YouTube URL → Video ID 변환
##################################################

def get_video_id(url):

    """
    유튜브 URL에서 영상 ID 추출
    """

    patterns = [
        r"youtu\.be/([^?&]+)",
        r"youtube\.com/watch\?v=([^?&]+)",
        r"youtube\.com/embed/([^?&]+)",
        r"youtube\.com/shorts/([^?&]+)"
    ]

    for pattern in patterns:

        result = re.search(
            pattern,
            url
        )

        if result:

            return result.group(1)

    return None



##################################################
# YouTube 댓글 수집
##################################################

def get_comments(
        youtube,
        video_id,
        max_comments=500,
        progress=None,
        status=None
):

    """
    YouTube Data API 댓글 수집

    return:
        [
            {
                comment:"",
                author:"",
                published:""
            }
        ]
    """

    comments = []

    next_page_token = None


    while len(comments) < max_comments:


        try:

            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()


        except Exception:

            break



        for item in response.get(
            "items",
            []
        ):


            snippet = (
                item["snippet"]
                ["topLevelComment"]
                ["snippet"]
            )


            comments.append(
                {
                    "comment":
                        snippet.get(
                            "textDisplay",
                            ""
                        ),

                    "author":
                        snippet.get(
                            "authorDisplayName",
                            ""
                        ),

                    "published":
                        snippet.get(
                            "publishedAt",
                            ""
                        )
                }
            )


            if len(comments) >= max_comments:

                break



        if progress:

            value = min(
                len(comments) / max_comments,
                1.0
            )

            progress.progress(
                int(value * 100)
            )


        if status:

            status.write(
                f"댓글 수집 중... {len(comments):,}/{max_comments:,}"
            )


        next_page_token = response.get(
            "nextPageToken"
        )


        if not next_page_token:

            break



    return comments



##################################################
# 한국어 형태소 분석기 준비
##################################################
##################################################
# 한국어 감성분석
##################################################

def sentiment_analysis(text):

    """
    간단한 한국어 감성분석

    return:
        긍정 / 부정 / 중립
    """

    if not isinstance(text, str):

        return "중립"


    text = text.lower()



    positive_words = [

        "좋다",
        "좋아요",
        "최고",
        "멋지다",
        "멋져",
        "대박",
        "감동",
        "재밌다",
        "재미있다",
        "웃기다",
        "행복",
        "사랑",
        "응원",
        "추천",
        "감사",
        "고맙",
        "잘한다",
        "훌륭",
        "완벽",
        "최애",
        "레전드",
        "짱"

    ]



    negative_words = [

        "싫다",
        "싫어요",
        "최악",
        "별로",
        "노잼",
        "재미없",
        "지루",
        "실망",
        "화난",
        "짜증",
        "답답",
        "못한다",
        "문제",
        "구리",
        "망했",
        "비추",
        "별루",
        "최악이다",
        "아쉽"

    ]



    positive_score = 0

    negative_score = 0



    for word in positive_words:

        if word in text:

            positive_score += 1



    for word in negative_words:

        if word in text:

            negative_score += 1



    if positive_score > negative_score:

        return "긍정"



    elif negative_score > positive_score:

        return "부정"



    else:

        return "중립"
      ##################################################
# 주요 키워드 추출
##################################################

def top_keywords(df):

    """
    댓글 데이터에서
    주요 명사 Top20 추출

    return:
        DataFrame
        단어 / 빈도
    """


    if df is None or len(df) == 0:

        return pd.DataFrame()



    okt = Okt()


    stopwords = [

        "영상",
        "댓글",
        "사람",
        "것",
        "수",
        "거",
        "때",
        "더",
        "좀",
        "진짜",
        "너무",
        "정말",
        "그냥",
        "오늘",
        "이번",
        "저",
        "나",
        "우리",
        "이",
        "그",
        "저것",
        "ㅋㅋ",
        "ㅎㅎ",
        "ㅠㅠ",
        "ㅜㅜ",
        "입니다",
        "합니다",
        "하세요"

    ]



    words = []



    for comment in df["comment"]:


        if not isinstance(
            comment,
            str
        ):

            continue



        nouns = okt.nouns(
            comment
        )


        for noun in nouns:


            if len(noun) < 2:

                continue



            if noun in stopwords:

                continue



            words.append(noun)



    if len(words) == 0:

        return pd.DataFrame()



    counter = Counter(words)



    result = pd.DataFrame(
        counter.most_common(20),
        columns=[
            "단어",
            "빈도"
        ]
    )


    return result
  ##################################################
# 댓글 작성 시간 분석 그래프
##################################################

def draw_time_chart(df, mode="일별"):

    """
    댓글 작성 시간 추이 그래프 생성

    mode:
        일별
        월별
        시간별

    return:
        Plotly Figure
    """



    if df is None or len(df) == 0:

        return None



    temp = df.copy()



    temp["published"] = pd.to_datetime(
        temp["published"],
        errors="coerce"
    )



    temp = temp.dropna(
        subset=[
            "published"
        ]
    )



    if mode == "일별":


        data = (
            temp
            .groupby(
                temp["published"].dt.date
            )
            .size()
            .reset_index()
        )


        data.columns = [
            "날짜",
            "댓글수"
        ]


        fig = px.line(
            data,
            x="날짜",
            y="댓글수",
            markers=True,
            title="일별 댓글 작성 추이"
        )



    elif mode == "월별":


        data = (
            temp
            .groupby(
                temp["published"]
                .dt
                .to_period("M")
                .astype(str)
            )
            .size()
            .reset_index()
        )


        data.columns = [
            "월",
            "댓글수"
        ]



        fig = px.bar(
            data,
            x="월",
            y="댓글수",
            title="월별 댓글 작성 추이"
        )



    elif mode == "시간별":


        data = (
            temp
            .groupby(
                temp["published"].dt.hour
            )
            .size()
            .reset_index()
        )


        data.columns = [
            "시간",
            "댓글수"
        ]



        fig = px.bar(
            data,
            x="시간",
            y="댓글수",
            title="시간대별 댓글 작성 패턴"
        )



    else:

        return None



    fig.update_layout(

        xaxis_title="",

        yaxis_title="댓글 수",

        hovermode="x unified"

    )


    return fig
  ##################################################
# 한글 폰트 다운로드
##################################################

def download_font():

    """
    GitHub에 업로드한
    나눔고딕 폰트 다운로드
    """

    font_dir = "fonts"

    font_path = os.path.join(
        font_dir,
        "NanumGothic.ttf"
    )


    if os.path.exists(font_path):

        return font_path



    os.makedirs(
        font_dir,
        exist_ok=True
    )


    # GitHub Raw 주소로 변경 필요
    font_url = (
        "https://raw.githubusercontent.com/"
        "YOUR_ID/YOUR_REPOSITORY/main/"
        "youtube/NanumGothic.ttf"
    )


    try:

        response = requests.get(
            font_url,
            timeout=10
        )


        response.raise_for_status()



        with open(
            font_path,
            "wb"
        ) as f:

            f.write(
                response.content
            )


        return font_path



    except Exception:


        return None




##################################################
# 한글 워드클라우드 생성
##################################################

def make_wordcloud(df):


    """
    댓글 DataFrame을 이용한
    한글 워드클라우드 생성

    return:
        WordCloud 객체
    """



    if df is None or len(df) == 0:

        return None



    okt = Okt()



    stopwords = [

        "영상",
        "댓글",
        "사람",
        "것",
        "수",
        "거",
        "너무",
        "진짜",
        "정말",
        "그냥",
        "ㅋㅋ",
        "ㅎㅎ",
        "ㅠㅠ",
        "ㅜㅜ"

    ]



    words = []



    for comment in df["comment"]:


        if not isinstance(
            comment,
            str
        ):

            continue



        nouns = okt.nouns(
            comment
        )



        for noun in nouns:


            if len(noun) < 2:

                continue



            if noun in stopwords:

                continue



            words.append(noun)



    if len(words) == 0:

        return None



    text = " ".join(
        words
    )



    font_path = download_font()



    if font_path is None:

        # 기본 폰트 fallback

        return WordCloud(
            width=1000,
            height=600,
            background_color="white"
        ).generate(text)



    wc = WordCloud(

        font_path=font_path,

        width=1200,

        height=700,

        background_color="white",

        max_words=200,

        colormap="viridis"

    )



    wc.generate(text)



    return wc

okt = Okt()
