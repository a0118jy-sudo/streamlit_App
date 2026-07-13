import streamlit as st
import requests
import random

st.set_page_config(
    page_title="🍽 오늘 뭐 먹지?",
    page_icon="🍜",
    layout="centered"
)

# -----------------------
# CSS (귀여운 디자인)
# -----------------------

st.markdown("""
<style>

.stApp{
background: linear-gradient(#FFF8F2,#FFEFE5);
}

.title{
font-size:40px;
font-weight:bold;
text-align:center;
color:#ff6b6b;
}

.subtitle{
text-align:center;
font-size:18px;
color:#555;
margin-bottom:20px;
}

.food-card{
background:white;
padding:25px;
border-radius:25px;
box-shadow:0px 4px 15px rgba(0,0,0,0.1);
}

.info{
font-size:18px;
}

.metric{
background:#FFF5F5;
padding:12px;
border-radius:15px;
margin-top:8px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🍽 오늘 뭐 먹지?</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>날씨에 맞는 메뉴를 추천해드려요 💖</div>", unsafe_allow_html=True)

# -----------------------
# 메뉴 데이터
# -----------------------

foods = {

"비":[
{
"name":"파전",
"image":"images/pajeon.jpg",
"cal":520,
"carb":"55g",
"protein":"17g",
"fat":"24g"
},
{
"name":"칼국수",
"image":"images/kalguksu.jpg",
"cal":480,
"carb":"68g",
"protein":"18g",
"fat":"12g"
}
],

"추움":[
{
"name":"김치찌개",
"image":"images/kimchi_jjigae.jpg",
"cal":430,
"carb":"22g",
"protein":"25g",
"fat":"18g"
},
{
"name":"삼계탕",
"image":"images/samgyetang.jpg",
"cal":600,
"carb":"20g",
"protein":"45g",
"fat":"30g"
}
],

"더움":[
{
"name":"냉면",
"image":"images/naengmyeon.jpg",
"cal":450,
"carb":"72g",
"protein":"17g",
"fat":"7g"
}
],

"맑음":[
{
"name":"비빔밥",
"image":"images/bibimbap.jpg",
"cal":560,
"carb":"73g",
"protein":"22g",
"fat":"15g"
},
{
"name":"순두부찌개",
"image":"images/sundubu.jpg",
"cal":390,
"carb":"18g",
"protein":"23g",
"fat":"15g"
}
],

"기본":[
{
"name":"우동",
"image":"images/udon.jpg",
"cal":480,
"carb":"70g",
"protein":"14g",
"fat":"10g"
}
]

}

# -----------------------
# 날씨 API
# -----------------------

API_KEY = st.secrets["OPENWEATHER_API_KEY"]

city = st.text_input("🏙 도시를 입력하세요", "Seoul")

def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    weather = data["weather"][0]["main"]
    temp = data["main"]["temp"]

    return weather, temp

# -----------------------
# 추천 버튼
# -----------------------

if st.button("🍀 오늘의 메뉴 추천"):

    result = get_weather(city)

    if result is None:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    weather, temp = result

    if weather == "Rain":
        category = "비"

    elif temp <= 10:
        category = "추움"

    elif temp >= 28:
        category = "더움"

    elif weather == "Clear":
        category = "맑음"

    else:
        category = "기본"

    food = random.choice(foods[category])

    st.success(f"현재 날씨 : {weather} / {temp:.1f}℃")

    st.markdown("<div class='food-card'>", unsafe_allow_html=True)

    st.image(food["image"], use_container_width=True)

    st.markdown(
        f"<h2 style='text-align:center;color:#ff6b6b'>{food['name']}</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
<div class='metric'>
🔥 <b>칼로리</b> : {food['cal']} kcal
</div>
""",
unsafe_allow_html=True
)

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("🍚 탄수화물", food["carb"])

    with col2:
        st.metric("🥩 단백질", food["protein"])

    with col3:
        st.metric("🥑 지방", food["fat"])

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🎲 다른 메뉴 추천"):

        food = random.choice(foods[category])

        st.image(food["image"], use_container_width=True)
        st.subheader(food["name"])
