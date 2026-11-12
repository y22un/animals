import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="멸종 위기 동물 데이터 탐색실",
    page_icon="🐾",
    layout="wide"
)


# =========================================================
# 2. 디자인 설정
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F1F7FD;
    }

    .main-title {
        background: linear-gradient(120deg, #174A78, #4F91C7);
        color: white;
        padding: 35px 30px;
        border-radius: 18px;
        margin-bottom: 22px;
    }

    .main-title h1 {
        color: white;
        font-size: 32px;
        margin-bottom: 8px;
    }

    .main-title p {
        color: #EAF4FC;
        font-size: 15px;
        margin-bottom: 0;
    }

    .section-title {
        color: #174A78;
        font-weight: 700;
        font-size: 23px;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .animal-name {
        color: #174A78;
        font-size: 21px;
        font-weight: 700;
    }

    .animal-scientific {
        color: #777777;
        font-size: 13px;
        font-style: italic;
    }

    .animal-emoji {
        font-size: 43px;
        text-align: center;
    }

    .book-note {
        background-color: #E8F3FC;
        padding: 16px;
        border-radius: 12px;
        color: #28577F;
        margin: 12px 0;
    }

    .cover-box {
        background: linear-gradient(135deg, #174A78, #76936C);
        color: white;
        border-radius: 20px;
        padding: 45px 30px;
        text-align: center;
        margin-bottom: 20px;
    }

    .cover-box h1 {
        color: white;
        font-size: 36px;
    }

    .cover-box p {
        color: #F0F8FF;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #D7E7F5;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 14px;
    }

    .small-caption {
        color: #58738D;
        font-size: 12px;
    }

    [data-testid="stSidebar"] {
        background-color: #E8F3FC;
    }

    .stButton > button, .stDownloadButton > button {
        background-color: #2F75B5;
        color: white;
        border: 1px solid #2F75B5;
        border-radius: 10px;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #174A78;
        color: white;
        border-color: #174A78;
    }

    [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #174A78;
        border-bottom-color: #2F75B5;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. 기본 데이터 설정
# =========================================================

COLUMN_LABELS = {
    "taxonid": "생물 고유 번호",
    "kingdom_name": "계",
    "phylum_name": "문",
    "class_name": "강",
    "order_name": "목",
    "family_name": "과",
    "genus_name": "속",
    "scientific_name": "학명",
    "taxonomic_authority": "학명 명명 정보",
    "infra_rank": "하위 분류 단계",
    "infra_name": "하위 분류 이름",
    "population": "개체군 정보",
    "category": "멸종 위험 등급",
    "main_common_name": "일반명"
}

COLUMN_DESCRIPTIONS = {
    "taxonid": "각 생물종을 구분하는 고유 식별 번호",
    "kingdom_name": "생물의 계를 나타내는 분류 정보",
    "phylum_name": "생물의 문을 나타내는 분류 정보",
    "class_name": "생물의 강을 나타내는 분류 정보",
    "order_name": "생물의 목을 나타내는 분류 정보",
    "family_name": "생물의 과를 나타내는 분류 정보",
    "genus_name": "생물의 속을 나타내는 분류 정보",
    "scientific_name": "국제적으로 사용하는 생물의 학술적 이름",
    "taxonomic_authority": "학명을 명명하거나 발표한 연구자 및 명명 정보",
    "infra_rank": "종 아래의 세부 분류 단계",
    "infra_name": "종 아래의 세부 분류 이름",
    "population": "평가 대상이 되는 개체군 또는 세부 집단 정보",
    "category": "IUCN 기준에 따른 멸종 위험 등급",
    "main_common_name": "일상적으로 사용하는 생물의 일반적인 이름"
}

RISK_NAMES = {
    "LC": "관심대상",
    "NT": "준위협",
    "VU": "취약",
    "EN": "위기",
    "CR": "위급",
    "DD": "정보부족",
    "EX": "절멸",
    "EW": "야생절멸",
    "LR/lc": "과거 등급(관심대상)",
    "LR/nt": "과거 등급(준위협)",
    "LR/cd": "과거 등급(보전의존)"
}

RISK_EMOJIS = {
    "LC": "🟢",
    "NT": "🟡",
    "VU": "🟠",
    "EN": "🔴",
    "CR": "🚨",
    "DD": "❔",
    "EX": "⚫",
    "EW": "🌑",
    "LR/lc": "📜",
    "LR/nt": "📜",
    "LR/cd": "📜"
}

CURRENT_RISK = ["LC", "NT", "VU", "EN", "CR"]

CLASS_EMOJIS = {
    "mammalia": "🐘",
    "aves": "🦜",
    "amphibia": "🐸",
    "reptilia": "🦎",
    "actinopterygii": "🐟",
    "chondrichthyes": "🦈",
    "insecta": "🦋",
    "arachnida": "🕷️",
    "gastropoda": "🐌",
    "malacostraca": "🦀",
    "cephalopoda": "🐙",
    "bivalvia": "🦪",
    "myriapoda": "🐛"
}

# 자주 사용되는 생물 분류명의 한국어 표기
# 확인되지 않은 명칭은 임의 번역하지 않고 영어 원어를 보존한다.
TAXON_KO = {
    "ANIMALIA": "동물계", "PLANTAE": "식물계", "FUNGI": "균계",
    "CHORDATA": "척삭동물문", "ARTHROPODA": "절지동물문",
    "MOLLUSCA": "연체동물문", "ANNELIDA": "환형동물문",
    "CNIDARIA": "자포동물문", "ECHINODERMATA": "극피동물문",
    "PORIFERA": "해면동물문", "PLATYHELMINTHES": "편형동물문",
    "NEMATODA": "선형동물문", "BRYOZOA": "태형동물문",
    "MAMMALIA": "포유강", "AVES": "조강", "AMPHIBIA": "양서강",
    "REPTILIA": "파충강", "ACTINOPTERYGII": "조기어강",
    "CHONDRICHTHYES": "연골어강", "INSECTA": "곤충강",
    "ARACHNIDA": "거미강", "GASTROPODA": "복족강",
    "MALACOSTRACA": "연갑강", "CEPHALOPODA": "두족강",
    "BIVALVIA": "이매패강", "MYRIAPODA": "다지강",
    "PRIMATES": "영장목", "CARNIVORA": "식육목",
    "RODENTIA": "쥐목", "CHIROPTERA": "익수목",
    "ARTIODACTYLA": "우제목", "PERISSODACTYLA": "기제목",
    "CETACEA": "고래목", "PROBOSCIDEA": "장비목",
    "PASSERIFORMES": "참새목", "ACCIPITRIFORMES": "수리목",
    "ANSERIFORMES": "기러기목", "GALLIFORMES": "닭목",
    "STRIGIFORMES": "올빼미목", "PSITTACIFORMES": "앵무목",
    "SQUAMATA": "뱀목", "TESTUDINES": "거북목",
    "CROCODYLIA": "악어목", "ANURA": "개구리목",
    "CAUDATA": "도롱뇽목", "LEPIDOPTERA": "나비목",
    "COLEOPTERA": "딱정벌레목", "HYMENOPTERA": "벌목",
    "DIPTERA": "파리목", "ORTHOPTERA": "메뚜기목",
    "DECAPODA": "십각목", "OCTOPODA": "문어목",
    "FELIDAE": "고양이과", "CANIDAE": "개과",
    "URSIDAE": "곰과", "ELEPHANTIDAE": "코끼리과",
    "CERVIDAE": "사슴과", "BOVIDAE": "소과",
    "MUSTELIDAE": "족제비과", "PHOCIDAE": "물범과",
    "DELPHINIDAE": "참돌고래과", "HOMINIDAE": "사람과",
    "PHASIANIDAE": "꿩과", "ACCIPITRIDAE": "수리과",
    "STRIGIDAE": "올빼미과", "PSITTACIDAE": "앵무과",
    "CHELONIIDAE": "바다거북과", "TESTUDINIDAE": "땅거북과",
    "SALAMANDRIDAE": "도롱뇽과", "RANIDAE": "개구리과",
    "RHINOCEROTIDAE": "코뿔소과", "GIRAFFIDAE": "기린과",
    "PANTHERA": "표범속", "CANIS": "개속", "URSUS": "곰속",
}

TAXON_COLUMNS = {
    "kingdom_name": "계", "phylum_name": "문",
    "class_name": "강", "order_name": "목",
    "family_name": "과", "genus_name": "속",
}

def display_taxon(value, rank=None):
    if pd.isna(value) or str(value).strip() == "":
        return "정보 없음"
    original = str(value).strip()
    korean = TAXON_KO.get(original.upper())
    if korean:
        return f"{korean} ({original})"
    return f"한국어 명칭 미등록 ({original})"

def display_animal_name(value):
    if pd.isna(value) or str(value).strip() == "":
        return "이름 정보 없음"
    original = str(value).strip()
    if any("가" <= ch <= "힣" for ch in original):
        return original
    return f"한국어 이름 미등록 ({original})"

def display_risk(code):
    if pd.isna(code):
        return "등급 정보 없음"
    code = str(code)
    return f"{RISK_NAMES.get(code, code)} ({code})"



def get_animal_emoji(class_name):
    """분류 단계에 맞는 이모지를 반환한다."""
    if pd.isna(class_name):
        return "🐾"

    name = str(class_name).lower().strip()

    for key, emoji in CLASS_EMOJIS.items():
        if key in name:
            return emoji

    return "🐾"


def get_risk_name(code):
    if pd.isna(code):
        return "등급 정보 없음"

    return RISK_NAMES.get(str(code), str(code))


def get_risk_emoji(code):
    if pd.isna(code):
        return "❔"

    return RISK_EMOJIS.get(str(code), "🐾")


def format_count(number):
    return f"{int(number):,}"


# =========================================================
# 4. 데이터 불러오기
# =========================================================

@st.cache_data
def load_csv(file_bytes):
    try:
        return pd.read_csv(
            BytesIO(file_bytes),
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            BytesIO(file_bytes),
            encoding="cp949"
        )


def find_local_csv():
    base_dir = Path(__file__).parent

    candidates = [
        base_dir / "threatened-species.csv",
        base_dir / "threatened-species(1).csv"
    ]

    for path in candidates:
        if path.exists():
            return path

    matches = sorted(
        base_dir.glob("threatened-species*.csv")
    )

    if matches:
        return matches[0]

    return None


# =========================================================
# 5. 사이드바
# =========================================================

st.sidebar.markdown("## 📖 동물 도감")
st.sidebar.caption("멸종 위기 동물을 찾아보세요.")

local_csv = find_local_csv()

if local_csv is not None:
    st.sidebar.success(f"파일 확인: {local_csv.name}")
    uploaded_file = st.sidebar.file_uploader(
        "다른 데이터 파일 사용하기",
        type=["csv"]
    )
else:
    st.sidebar.warning("데이터 파일을 업로드해 주세요.")
    uploaded_file = st.sidebar.file_uploader(
        "threatened-species.csv",
        type=["csv"]
    )


# =========================================================
# 6. 데이터 읽기 및 전처리
# =========================================================

try:
    if uploaded_file is not None:
        original_df = load_csv(uploaded_file.getvalue())
        file_name = uploaded_file.name

    elif local_csv is not None:
        original_df = load_csv(local_csv.read_bytes())
        file_name = local_csv.name

    else:
        st.markdown("""
        <div class="cover-box">
            <h1>🐾 멸종 위기 동물 도감</h1>
            <p>사라져 가는 생명들을 데이터로 만나보세요.</p>
            <p>동물의 이름을 검색하고, 분류와 멸종 위험 등급을 살펴볼 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(
            "앱과 같은 폴더에 threatened-species.csv를 넣거나 "
            "왼쪽 메뉴에서 CSV 파일을 업로드해 주세요."
        )
        st.stop()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


required_columns = [
    "taxonid",
    "kingdom_name",
    "phylum_name",
    "class_name",
    "order_name",
    "family_name",
    "genus_name",
    "scientific_name",
    "taxonomic_authority",
    "infra_rank",
    "infra_name",
    "population",
    "category",
    "main_common_name"
]

missing_columns = [
    col for col in required_columns
    if col not in original_df.columns
]

if missing_columns:
    st.error(
        "필요한 컬럼이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# 원본 데이터는 그대로 보관
original_df = original_df.copy()

# 동물계만 추출
animal_df = original_df[
    original_df["kingdom_name"]
    .astype("string")
    .str.strip()
    .str.upper()
    .eq("ANIMALIA")
].copy()

# 중복 확인
duplicate_count = int(
    animal_df.duplicated(subset=["taxonid"]).sum()
)

# 고유 번호 기준 중복 제거
animal_df = animal_df.drop_duplicates(
    subset=["taxonid"],
    keep="first"
).copy()

# 등급 앞뒤 공백 제거
animal_df["category"] = (
    animal_df["category"]
    .astype("string")
    .str.strip()
)

# 일반명 결측치 처리: 학명은 유지하고 표시용 이름만 보완
animal_df["표시 이름"] = animal_df["main_common_name"].fillna(
    animal_df["scientific_name"]
)

animal_df["표시 이름"] = (
    animal_df["표시 이름"]
    .fillna("이름 정보 없음")
    .astype(str)
)

# 주요 등급 데이터
current_df = animal_df[
    animal_df["category"].isin(CURRENT_RISK)
].copy()

current_df["등급 이름"] = (
    current_df["category"].map(RISK_NAMES)
)

# 분류별 이모지
animal_df["동물 이모지"] = animal_df["class_name"].apply(
    get_animal_emoji
)

current_df["동물 이모지"] = current_df["class_name"].apply(
    get_animal_emoji
)


# =========================================================
# 7. 상단 제목
# =========================================================

st.markdown("""
<div class="main-title">
    <h1>🐾 멸종 위기 동물 데이터 탐색실</h1>
    <p>사라져 가는 생명들을 한 종씩 만나고, 데이터로 이해하는 동물 도감</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 8. 책 형식 메뉴
# =========================================================

tab_cover, tab_book, tab_explore, tab_data = st.tabs([
    "📕 책 표지",
    "🐾 동물 도감",
    "🌿 데이터 탐색",
    "📚 자료실"
])


# =========================================================
# 9. 책 표지
# =========================================================

with tab_cover:

    st.markdown("""
    <div class="cover-box">
        <h1>🌏 멸종 위기 동물 도감</h1>
        <p>우리와 함께 살아가는 동물들의 이야기</p>
        <p>한 종의 이름을 기억하는 것에서 보호는 시작됩니다.</p>
        <br>
        <h2>📖 WILDLIFE ENCYCLOPEDIA</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📌 이 책에 담긴 데이터")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "전체 생물 데이터",
            format_count(len(original_df))
        )

    with c2:
        st.metric(
            "동물계 데이터",
            format_count(len(animal_df))
        )

    with c3:
        st.metric(
            "주요 위험 등급 데이터",
            format_count(len(current_df))
        )

    with c4:
        st.metric(
            "동물 분류 종류",
            format_count(
                animal_df["class_name"].nunique()
            )
        )

    st.markdown("""
    <div class="book-note">
        <b>📖 도감 이용 방법</b><br>
        1. 동물 도감에서 이름을 검색합니다.<br>
        2. 강과 멸종 위험 등급을 선택해 동물을 찾습니다.<br>
        3. 동물 카드를 펼쳐 상세 정보를 확인합니다.<br>
        4. 데이터 탐색에서 멸종 위험 등급의 분포를 살펴봅니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚦 멸종 위험 등급 안내")

    risk_cols = st.columns(5)

    risk_items = [
        ("LC", "관심대상", "🟢"),
        ("NT", "준위협", "🟡"),
        ("VU", "취약", "🟠"),
        ("EN", "위기", "🔴"),
        ("CR", "위급", "🚨")
    ]

    for col, (code, name, emoji) in zip(risk_cols, risk_items):
        with col:
            st.markdown(f"### {emoji}")
            st.markdown(f"**{name}**")
            st.caption(code)

    st.caption(
        f"현재 사용 중인 데이터 파일: {file_name}"
    )


# =========================================================
# 10. 동물 도감
# =========================================================

with tab_book:

    st.markdown(
        '<div class="section-title">🐾 동물 한 종씩 만나보기</div>',
        unsafe_allow_html=True
    )

    st.write(
        "검색어를 입력하거나 분류와 위험 등급을 선택해 원하는 동물을 찾아보세요."
    )

    # -----------------------------------------------------
    # 검색 기능
    # -----------------------------------------------------

    search_col, clear_col = st.columns([5, 1])

    with search_col:
        search_text = st.text_input(
            "🔎 동물 이름 검색",
            placeholder="예: 호랑이, tiger, Panthera tigris",
            key="animal_search"
        )

    with clear_col:
        st.write("")
        st.write("")
        if st.button("검색 초기화", use_container_width=True):
            st.session_state["animal_search"] = ""
            st.rerun()

    # -----------------------------------------------------
    # 필터
    # -----------------------------------------------------

    filter1, filter2, filter3 = st.columns(3)

    class_values = sorted(
        animal_df["class_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with filter1:
        class_display = {"전체": "전체"}
        class_display.update({v: display_taxon(v, "강") for v in class_values})
        selected_class = st.selectbox(
            "🧬 동물 분류(강)",
            ["전체"] + class_values,
            format_func=lambda value: class_display.get(value, value)
        )

    category_values = [
        code for code in
        ["LC", "NT", "VU", "EN", "CR", "DD", "EX", "EW",
         "LR/lc", "LR/nt", "LR/cd"]
        if code in animal_df["category"].dropna().unique()
    ]

    with filter2:
        selected_category = st.selectbox(
            "🚦 멸종 위험 등급",
            ["전체"] + category_values,
            format_func=lambda x: (
                "전체 등급"
                if x == "전체"
                else f"{get_risk_emoji(x)} {get_risk_name(x)} ({x})"
            )
        )

    with filter3:
        sort_option = st.selectbox(
            "정렬 방법",
            [
                "이름순",
                "위험 등급순",
                "학명순"
            ]
        )

    # -----------------------------------------------------
    # 검색 결과 필터링
    # -----------------------------------------------------

    result_df = animal_df.copy()

    if search_text.strip():
        search_lower = search_text.strip().lower()

        common_match = (
            result_df["표시 이름"]
            .astype(str)
            .str.lower()
            .str.contains(search_lower, na=False)
        )

        scientific_match = (
            result_df["scientific_name"]
            .astype(str)
            .str.lower()
            .str.contains(search_lower, na=False)
        )

        result_df = result_df[
            common_match | scientific_match
        ]

    if selected_class != "전체":
        result_df = result_df[
            result_df["class_name"].astype(str)
            == selected_class
        ]

    if selected_category != "전체":
        result_df = result_df[
            result_df["category"] == selected_category
        ]

    # -----------------------------------------------------
    # 정렬
    # -----------------------------------------------------

    if sort_option == "이름순":
        result_df = result_df.sort_values(
            "표시 이름",
            key=lambda x: x.astype(str).str.lower()
        )

    elif sort_option == "학명순":
        result_df = result_df.sort_values(
            "scientific_name",
            key=lambda x: x.fillna("").astype(str).str.lower()
        )

    elif sort_option == "위험 등급순":
        result_df["_등급 순서"] = result_df["category"].map({
            "CR": 1,
            "EN": 2,
            "VU": 3,
            "NT": 4,
            "LC": 5
        }).fillna(99)

        result_df = result_df.sort_values(
            "_등급 순서"
        )

    result_df = result_df.reset_index(drop=True)

    st.divider()

    st.markdown(
        f"### 🔍 검색 결과: **{len(result_df):,}종**"
    )

    # -----------------------------------------------------
    # 페이지 나누기
    # -----------------------------------------------------

    items_per_page = 12

    total_pages = max(
        1,
        (len(result_df) + items_per_page - 1)
        // items_per_page
    )

    page_number = st.number_input(
        "도감 페이지",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

    start_index = (int(page_number) - 1) * items_per_page
    end_index = start_index + items_per_page

    page_df = result_df.iloc[start_index:end_index]

    st.caption(
        f"{start_index + 1:,}번부터 "
        f"{min(end_index, len(result_df)):,}번까지 표시 중"
        if len(result_df) > 0
        else "검색 결과가 없습니다."
    )

    if len(page_df) == 0:
        st.warning(
            "검색 결과가 없습니다. 다른 이름이나 검색 조건을 사용해 보세요."
        )

    # -----------------------------------------------------
    # 동물 카드
    # -----------------------------------------------------

    cards = st.columns(2)

    for index, (_, animal) in enumerate(page_df.iterrows()):

        card_col = cards[index % 2]

        with card_col:
            with st.container(border=True):

                emoji = get_animal_emoji(
                    animal["class_name"]
                )

                category = animal["category"]

                risk_emoji = get_risk_emoji(category)
                risk_name = get_risk_name(category)

                common_name = display_animal_name(animal["표시 이름"])

                scientific_name = animal["scientific_name"]

                if pd.isna(scientific_name):
                    scientific_name = "학명 정보 없음"

                st.markdown(
                    f'<div class="animal-emoji">{emoji}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="animal-name">{common_name}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="animal-scientific">{scientific_name}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"**{risk_emoji} {risk_name} ({category if pd.notna(category) else '정보 없음'})**"
                )

                class_name = (
                    str(animal["class_name"])
                    if pd.notna(animal["class_name"])
                    else "정보 없음"
                )

                st.caption(
                    f"강: {display_taxon(class_name, '강')}"
                )

                with st.expander("📖 상세 정보 펼쳐보기"):

                    details = [
                        ("생물 고유 번호", "taxonid"),
                        ("계", "kingdom_name"),
                        ("문", "phylum_name"),
                        ("강", "class_name"),
                        ("목", "order_name"),
                        ("과", "family_name"),
                        ("속", "genus_name"),
                        ("학명", "scientific_name"),
                        ("학명 명명 정보", "taxonomic_authority"),
                        ("하위 분류 단계", "infra_rank"),
                        ("하위 분류 이름", "infra_name"),
                        ("개체군 정보", "population"),
                        ("일반명", "main_common_name")
                    ]

                    for label, column in details:
                        value = animal[column]

                        if pd.isna(value) or str(value).strip() == "":
                            value = "정보 없음"

                        if column in TAXON_COLUMNS:
                            value = display_taxon(value, TAXON_COLUMNS[column])
                        elif column == "main_common_name":
                            value = display_animal_name(value)
                        elif column == "category":
                            value = display_risk(value)

                        st.write(f"**{label}:** {value}")

                    st.caption(
                        "이 정보는 제공된 데이터 파일을 바탕으로 표시됩니다."
                    )


# =========================================================
# 11. 데이터 탐색
# =========================================================

with tab_explore:

    st.markdown(
        '<div class="section-title">🌿 멸종 위험 데이터 탐색</div>',
        unsafe_allow_html=True
    )

    st.write(
        "동물의 멸종 위험 등급과 생물학적 분류 사이의 관계를 그래프로 살펴봅니다."
    )

    if len(current_df) == 0:
        st.warning("현재 주요 위험 등급에 해당하는 데이터가 없습니다.")
    else:

        # 등급별 개수
        risk_count = (
            current_df["category"]
            .value_counts()
            .reindex(CURRENT_RISK, fill_value=0)
            .rename_axis("등급")
            .reset_index(name="동물 수")
        )

        risk_count["등급 이름"] = (
            risk_count["등급"].map(RISK_NAMES)
        )

        risk_count["표시 등급"] = (
            risk_count["등급"].map(
                lambda x: f"{RISK_EMOJIS[x]} {RISK_NAMES[x]}"
            )
        )

        st.subheader("1. 멸종 위험 등급별 동물 수")

        fig_count = px.bar(
            risk_count,
            x="표시 등급",
            y="동물 수",
            text="동물 수",
            title="멸종 위험 등급별 동물 수",
            labels={
                "표시 등급": "멸종 위험 등급",
                "동물 수": "동물 개수"
            },
            color_discrete_sequence=["#174A78", "#2F75B5", "#5B9BD5", "#8DBCE6", "#B7D5EF"]
        )

        fig_count.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        st.plotly_chart(
            fig_count,
            use_container_width=True
        )

        st.subheader("2. 멸종 위험 등급별 비율")

        fig_pie = px.pie(
            risk_count,
            names="표시 등급",
            values="동물 수",
            hole=0.45,
            title="멸종 위험 등급별 비율",
            color_discrete_sequence=["#174A78", "#2F75B5", "#5B9BD5", "#8DBCE6", "#B7D5EF"]
        )

        fig_pie.update_traces(
            textinfo="label+percent"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

        st.divider()

        # 분류별 그래프
        classification_options = {
            "강": "class_name",
            "목": "order_name",
            "과": "family_name"
        }

        selected_level = st.selectbox(
            "분석할 분류 단계",
            list(classification_options.keys())
        )

        selected_column = classification_options[selected_level]

        temp = current_df.copy()

        temp[selected_column] = (
            temp[selected_column]
            .fillna("정보 없음")
            .astype(str)
        )

        top_groups = (
            temp[selected_column]
            .value_counts()
            .head(15)
            .index
            .tolist()
        )

        temp["분류 이름"] = temp[selected_column].where(
            temp[selected_column].isin(top_groups),
            "기타"
        )
        temp["분류 이름"] = temp["분류 이름"].apply(
            lambda value: "기타" if value == "기타"
            else display_taxon(value, selected_level)
        )

        graph_data = pd.crosstab(
            temp["분류 이름"],
            temp["category"]
        )

        graph_data = graph_data.reindex(
            columns=CURRENT_RISK,
            fill_value=0
        )

        graph_long = graph_data.reset_index().melt(
            id_vars="분류 이름",
            var_name="등급",
            value_name="동물 수"
        )

        graph_long["등급 이름"] = (
            graph_long["등급"].map(RISK_NAMES)
        )

        st.subheader(
            f"3. 생물의 {selected_level}에 따른 멸종 위험 등급"
        )

        fig_group = px.bar(
            graph_long,
            x="분류 이름",
            y="동물 수",
            color="등급 이름",
            barmode="stack",
            title=f"{selected_level}별 멸종 위험 등급 분포",
            labels={
                "분류 이름": f"생물의 {selected_level}",
                "동물 수": "동물 개수",
                "등급 이름": "멸종 위험 등급"
            },
            color_discrete_sequence=["#174A78", "#2F75B5", "#5B9BD5", "#8DBCE6", "#B7D5EF"]
        )

        fig_group.update_layout(
            xaxis_title=f"생물의 {selected_level}",
            yaxis_title="동물 개수",
            legend_title="멸종 위험 등급"
        )

        st.plotly_chart(
            fig_group,
            use_container_width=True
        )

        st.subheader("4. 분류별 위험 등급 비교표")

        count_table = graph_data.copy()
        count_table.columns = [
            RISK_NAMES.get(col, col) + " 동물 수"
            for col in count_table.columns
        ]

        count_table["전체 동물 수"] = count_table.sum(axis=1)

        percent_table = graph_data.div(
            graph_data.sum(axis=1).replace(0, 1),
            axis=0
        ) * 100

        percent_table.columns = [
            RISK_NAMES.get(col, col) + " 비율(%)"
            for col in percent_table.columns
        ]

        st.markdown("**분류별 동물 수**")
        st.dataframe(
            count_table,
            use_container_width=True
        )

        st.markdown("**분류별 위험 등급 비율**")
        st.dataframe(
            percent_table.round(1),
            use_container_width=True
        )

        st.info(
            "그래프의 '기타'는 해당 분류 단계에서 데이터 수가 많은 "
            "상위 15개 분류에 포함되지 않은 나머지 분류를 합친 것입니다."
        )

    st.warning(
        "분류 단계에 따른 위험 등급 분포는 관계를 보여 줄 뿐, "
        "특정 분류가 멸종 위험의 직접적인 원인이라는 뜻은 아닙니다."
    )


# =========================================================
# 12. 자료실
# =========================================================

with tab_data:

    st.markdown(
        '<div class="section-title">📚 데이터 자료실</div>',
        unsafe_allow_html=True
    )

    st.write(
        "원본 데이터의 구조와 결측치, 전처리 결과를 확인할 수 있습니다."
    )

    st.subheader("1. 원본 데이터 정보")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.metric(
            "원본 데이터 수",
            format_count(len(original_df))
        )

    with info2:
        st.metric(
            "동물계 데이터 수",
            format_count(len(animal_df))
        )

    with info3:
        st.metric(
            "중복 제거 개수",
            format_count(duplicate_count)
        )

    st.divider()

    st.subheader("2. 컬럼 설명")

    column_rows = []

    for col in original_df.columns:
        column_rows.append({
            "컬럼 이름": col,
            "우리말 의미": COLUMN_LABELS.get(col, col),
            "설명": COLUMN_DESCRIPTIONS.get(col, "설명 없음"),
            "데이터 유형": (
                "숫자형"
                if pd.api.types.is_numeric_dtype(original_df[col])
                else "문자형"
            )
        })

    st.dataframe(
        pd.DataFrame(column_rows),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("3. 결측치 확인")

    missing_table = pd.DataFrame({
        "컬럼 이름": original_df.columns,
        "우리말 의미": [
            COLUMN_LABELS.get(col, col)
            for col in original_df.columns
        ],
        "결측치 개수": original_df.isna().sum().values,
        "결측치 비율(%)": (
            original_df.isna().mean().values * 100
        ).round(2)
    })

    missing_table = missing_table.sort_values(
        "결측치 개수",
        ascending=False
    )

    st.dataframe(
        missing_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("4. 멸종 위험 등급별 데이터")

    category_table = (
        animal_df["category"]
        .value_counts(dropna=False)
        .rename_axis("등급 코드")
        .reset_index(name="동물 수")
    )

    category_table["등급 이름"] = (
        category_table["등급 코드"]
        .apply(get_risk_name)
    )

    st.dataframe(
        category_table[
            ["등급 코드", "등급 이름", "동물 수"]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("5. 전처리 데이터 다운로드")

    st.write(
        f"현재 주요 위험 등급(LC, NT, VU, EN, CR)에 해당하는 "
        f"동물은 **{len(current_df):,}개**입니다."
    )

    download_df = current_df.copy()

    csv_bytes = download_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 전처리된 동물 데이터 다운로드",
        data=csv_bytes,
        file_name="전처리된_멸종위기동물.csv",
        mime="text/csv"
    )


# =========================================================
# 13. 하단 안내
# =========================================================

st.divider()

st.caption(
    "🐾 멸종 위기 동물 데이터 탐색실 | 데이터 탐색과 학습을 위한 앱"
)

st.caption(
    "이 앱의 데이터는 생물종의 분류 정보와 멸종 위험 등급을 보여 줍니다. "
    "분석 결과만으로 멸종 위험의 원인을 확정할 수는 없습니다."
)
