import streamlit as st
import random

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="🍽 오늘 뭐 먹지?",
    page_icon="🍜",
    layout="centered"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(to bottom,#FFF8F0,#FFE9F3);
}

.title{
    font-size:42px;
    color:#ff6b81;
    text-align:center;
    font-weight:bold;
}

.subtitle{
    text-align:center;
    color:#666;
    font-size:18px;
    margin-bottom:30px;
}

.card{
    background:white;
    padding:20px;
    border-radius:20px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.15);
}

.stButton>button{
    width:100%;
    border-radius:12px;
    background:#ff8fab;
    color:white;
    font-size:18px;
    border:none;
    padding:10px;
}

.stButton>button:hover{
    background:#ff6b81;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🍽 오늘 뭐 먹지?</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>날씨에 맞는 메뉴를 추천해 드려요 ☀️🌧️❄️</div>", unsafe_allow_html=True)

# -------------------------
# 음식 데이터
# -------------------------

foods = {

"☀️ 맑음":[

{
"name":"비빔밥",
"image":"images/bibimbap.jpg",
"cal":560,
"carb":"73g",
"protein":"22g",
"fat":"15g",
"reason":"신선한 채소가 가득해서 맑은 날과 잘 어울려요!"
},

{
"name":"순두부찌개",
"image":"images/sundubu.jpg",
"cal":390,
"carb":"18g",
"protein":"23g",
"fat":"15g",
"reason":"든든하고 부담 없이 즐길 수 있어요."
}

],

"🌧️ 비":[

{
"name":"파전",
"image":"images/pajeon.jpg",
"cal":520,
"carb":"55g",
"protein":"17g",
"fat":"24g",
"reason":"비 오는 날 가장 인기 있는 메뉴예요!"
},

{
"name":"칼국수",
"image":"images/kalguksu.jpg",
"cal":480,
"carb":"68g",
"protein":"18g",
"fat":"12g",
"reason":"따뜻한 국물이 몸을 녹여줘요."
}

],

"❄️ 추움":[

{
"name":"김치찌개",
"image":"images/kimchi.jpg",
"cal":430,
"carb":"22g",
"protein":"25g",
"fat":"18g",
"reason":"매콤하고 따뜻해서 추운 날 딱!"
},

{
"name":"삼계탕",
"image":"images/samgyetang.jpg",
"cal":610,
"carb":"20g",
"protein":"45g",
"fat":"28g",
"reason":"몸보신하기 좋은 메뉴예요."
}

],

"🔥 더움":[

{
"name":"냉면",
"image":"images/naengmyeon.jpg",
"cal":450,
"carb":"72g",
"protein":"17g",
"fat":"7g",
"reason":"시원한 냉면으로 더위를 날려보세요!"
}

],

"☁️ 흐림":[

{
"name":"우동",
"image":"images/udon.jpg",
"cal":480,
"carb":"70g",
"protein":"14g",
"fat":"10g",
"reason":"따뜻한 국물이 기분을 편안하게 해줘요."
}

]

}

# -------------------------
# 날씨 선택
# -------------------------

weather = st.selectbox(
    "🌈 오늘의 날씨를 선택하세요",
    list(foods.keys())
)

# -------------------------
# 추천 버튼
# -------------------------

if st.button("🍀 메뉴 추천받기"):

    food = random.choice(foods[weather])

    st.balloons()

    st.markdown("---")

    st.image(food["image"], use_container_width=True)

    st.markdown(
        f"<h2 style='text-align:center;color:#ff6b81'>{food['name']}</h2>",
        unsafe_allow_html=True
    )

    st.success(food["reason"])

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("🔥 칼로리", f'{food["cal"]} kcal')

    with col2:
        st.metric("🍚 탄수화물", food["carb"])

    with col3:
        st.metric("🥩 단백질", food["protein"])

    st.metric("🥑 지방", food["fat"])

    if st.button("🎲 다른 메뉴 추천"):

        food = random.choice(foods[weather])

        st.image(food["image"], use_container_width=True)

        st.subheader(food["name"])
