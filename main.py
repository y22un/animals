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

st.title("🐾 멸종 위기 동물 데이터 탐색실")
st.caption(
    "생물의 분류 특성과 멸종 위험 등급을 데이터로 탐색하는 실습 공간입니다."
)

st.divider()


# =========================================================
# 2. 기본 설정
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

CATEGORY_LABELS = {
    "LC": "관심대상",
    "NT": "준위협",
    "VU": "취약",
    "EN": "위기",
    "CR": "위급",
    "DD": "정보부족",
    "EX": "절멸",
    "EW": "야생절멸",
    "LR/lc": "과거 등급(LR/lc)",
    "LR/nt": "과거 등급(LR/nt)",
    "LR/cd": "과거 등급(LR/cd)"
}

CURRENT_RISK_ORDER = ["LC", "NT", "VU", "EN", "CR"]

CURRENT_RISK_LABELS = {
    "LC": "관심대상",
    "NT": "준위협",
    "VU": "취약",
    "EN": "위기",
    "CR": "위급"
}

HISTORICAL_CATEGORIES = ["LR/lc", "LR/nt", "LR/cd"]

EXCLUDED_CATEGORIES = ["DD", "EX", "EW"]

COLUMN_DESCRIPTIONS = {
    "taxonid": "각 생물종을 구분하기 위한 고유 식별 번호",
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


# =========================================================
# 3. 데이터 불러오기
# =========================================================

@st.cache_data
def load_csv(file_bytes):
    """CSV 파일을 읽어 데이터프레임으로 반환한다."""
    try:
        return pd.read_csv(BytesIO(file_bytes), encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(BytesIO(file_bytes), encoding="cp949")


def find_local_csv():
    """앱 폴더에 저장된 CSV 파일을 찾는다."""
    base_dir = Path(__file__).parent

    candidates = [
        base_dir / "threatened-species.csv",
        base_dir / "threatened-species(1).csv"
    ]

    for path in candidates:
        if path.exists():
            return path

    # 비슷한 이름의 CSV 파일도 확인한다.
    matches = sorted(base_dir.glob("threatened-species*.csv"))

    if matches:
        return matches[0]

    return None


local_csv = find_local_csv()

st.sidebar.header("📁 데이터 파일")

if local_csv is not None:
    st.sidebar.success(f"파일을 찾았습니다: {local_csv.name}")
    uploaded_file = st.sidebar.file_uploader(
        "다른 CSV 파일 사용하기",
        type=["csv"]
    )
else:
    st.sidebar.warning("CSV 파일을 업로드해 주세요.")
    uploaded_file = st.sidebar.file_uploader(
        "threatened-species.csv 업로드",
        type=["csv"]
    )


try:
    if uploaded_file is not None:
        raw_df = load_csv(uploaded_file.getvalue())
        file_name = uploaded_file.name
    elif local_csv is not None:
        raw_df = load_csv(local_csv.read_bytes())
        file_name = local_csv.name
    else:
        st.info(
            "앱과 같은 폴더에 threatened-species.csv 파일을 넣거나 "
            "왼쪽 메뉴에서 CSV 파일을 업로드해 주세요."
        )
        st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# =========================================================
# 4. 데이터 기본 확인
# =========================================================

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
    if col not in raw_df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 컬럼이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()

if raw_df.empty:
    st.error("CSV 파일에 데이터가 없습니다.")
    st.stop()


# 원본 데이터는 변경하지 않고 별도로 보관한다.
original_df = raw_df.copy()

# 분석에 필요한 데이터만 별도로 생성한다.
animal_df = original_df[
    original_df["kingdom_name"]
    .astype("string")
    .str.strip()
    .str.upper()
    .eq("ANIMALIA")
].copy()

# =========================================================
# 5. 중복 데이터 확인 및 제거
# =========================================================

exact_duplicate_count = int(animal_df.duplicated().sum())

taxonid_duplicate_count = int(
    animal_df.duplicated(subset=["taxonid"]).sum()
)

scientific_name_duplicate_count = int(
    animal_df["scientific_name"].duplicated().sum()
)

# 동일한 고유 번호를 가진 행은 첫 번째 행만 유지한다.
animal_no_duplicates = animal_df.drop_duplicates(
    subset=["taxonid"],
    keep="first"
).copy()

removed_duplicate_count = (
    len(animal_df) - len(animal_no_duplicates)
)


# =========================================================
# 6. 멸종 위험 등급 전처리
# =========================================================

animal_no_duplicates["category"] = (
    animal_no_duplicates["category"]
    .astype("string")
    .str.strip()
)

# 현재 사용하는 주요 멸종 위험 등급만 선택한다.
current_risk_df = animal_no_duplicates[
    animal_no_duplicates["category"].isin(CURRENT_RISK_ORDER)
].copy()

# 한국어 등급 이름을 추가한다.
current_risk_df["멸종 위험 등급"] = (
    current_risk_df["category"].map(CURRENT_RISK_LABELS)
)

# 학습 및 분석에 사용할 수 있도록 별도 데이터 생성
preprocessed_df = current_risk_df.copy()


# =========================================================
# 7. 제외 데이터 확인
# =========================================================

category_counts = animal_no_duplicates["category"].value_counts(
    dropna=False
)

dd_count = int(
    animal_no_duplicates["category"].eq("DD").sum()
)

ex_count = int(
    animal_no_duplicates["category"].eq("EX").sum()
)

ew_count = int(
    animal_no_duplicates["category"].eq("EW").sum()
)

historical_count = int(
    animal_no_duplicates["category"]
    .isin(HISTORICAL_CATEGORIES)
    .sum()
)

current_count = len(current_risk_df)

missing_category_count = int(
    animal_no_duplicates["category"].isna().sum()
)

known_category_count = (
    dd_count
    + ex_count
    + ew_count
    + historical_count
    + current_count
    + missing_category_count
)

other_category_count = (
    len(animal_no_duplicates) - known_category_count
)


# =========================================================
# 8. 사이드바 메뉴
# =========================================================

st.sidebar.divider()

page = st.sidebar.radio(
    "이동할 화면",
    [
        "📘 데이터 소개",
        "🧹 데이터 전처리",
        "📊 데이터 탐색"
    ]
)


# =========================================================
# 9. 공통 함수
# =========================================================

def format_number(value):
    return f"{int(value):,}"


def get_type_name(series):
    """pandas 자료형을 우리말로 표시한다."""
    dtype = str(series.dtype)

    if "int" in dtype:
        return "정수형"
    elif "float" in dtype:
        return "실수형"
    elif "bool" in dtype:
        return "논리형"
    elif "datetime" in dtype:
        return "날짜형"
    else:
        return "문자형"


def get_category_name(code):
    if pd.isna(code):
        return "정보 없음"

    return CATEGORY_LABELS.get(str(code), str(code))


def make_category_table(data):
    """멸종 위험 등급별 개수와 비율을 계산한다."""
    counts = data["category"].value_counts(dropna=False)

    result = counts.rename("동물 수").to_frame()
    result["비율(%)"] = (
        result["동물 수"] / len(data) * 100
    ).round(2)

    result = result.reset_index()
    result.columns = ["등급 코드", "동물 수", "비율(%)"]

    result["등급 이름"] = result["등급 코드"].apply(
        get_category_name
    )

    return result[
        ["등급 코드", "등급 이름", "동물 수", "비율(%)"]
    ]


def make_group_analysis(data, column, label, top_n=15):
    """분류 단계별 멸종 위험 등급 분포를 계산한다."""

    temp = data.copy()

    temp[column] = (
        temp[column]
        .fillna("정보 없음")
        .astype(str)
    )

    # 데이터가 많은 상위 분류만 그래프로 표시한다.
    top_groups = (
        temp[column]
        .value_counts()
        .head(top_n)
        .index
        .tolist()
    )

    temp["표시 분류"] = temp[column].where(
        temp[column].isin(top_groups),
        "기타"
    )

    # 등급별 개수
    count_table = pd.crosstab(
        temp["표시 분류"],
        temp["category"]
    )

    # 등급별 비율
    percent_table = (
        pd.crosstab(
            temp["표시 분류"],
            temp["category"],
            normalize="index"
        ) * 100
    ).round(1)

    # 등급 순서 정리
    available_categories = [
        category
        for category in CURRENT_RISK_ORDER
        if category in count_table.columns
    ]

    count_table = count_table.reindex(
        columns=available_categories,
        fill_value=0
    )

    percent_table = percent_table.reindex(
        columns=available_categories,
        fill_value=0
    )

    # 분류별 전체 개체 수
    group_sizes = (
        temp["표시 분류"]
        .value_counts()
        .rename("전체 동물 수")
    )

    count_table = count_table.join(group_sizes)
    percent_table = percent_table.join(group_sizes)

    # 그래프용 데이터
    graph_data = count_table.reset_index().melt(
        id_vars=["표시 분류", "전체 동물 수"],
        value_vars=available_categories,
        var_name="멸종 위험 등급",
        value_name="동물 수"
    )

    graph_data["등급 이름"] = (
        graph_data["멸종 위험 등급"]
        .map(CURRENT_RISK_LABELS)
    )

    # 표의 열 이름을 우리말로 변경
    count_display = count_table.copy()
    count_display.columns = [
        f"{CURRENT_RISK_LABELS.get(col, col)} 동물 수"
        if col != "전체 동물 수"
        else col
        for col in count_display.columns
    ]

    percent_display = percent_table.copy()
    percent_display.columns = [
        f"{CURRENT_RISK_LABELS.get(col, col)} 비율(%)"
        if col != "전체 동물 수"
        else col
        for col in percent_display.columns
    ]

    return graph_data, count_display, percent_display


# =========================================================
# 10. 데이터 소개 화면
# =========================================================

if page == "📘 데이터 소개":

    st.header("📘 데이터 소개")

    st.write(
        "이 데이터는 생물종의 분류 정보와 멸종 위험 등급을 "
        "포함하고 있습니다. 이번 탐구에서는 동물계에 해당하는 "
        "데이터를 중심으로 분석합니다."
    )

    st.caption(f"사용 중인 파일: {file_name}")

    # 기본 지표
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "전체 데이터 수",
            format_number(len(original_df))
        )

    with col2:
        st.metric(
            "전체 컬럼 수",
            format_number(len(original_df.columns))
        )

    with col3:
        st.metric(
            "동물계 데이터 수",
            format_number(len(animal_df))
        )

    with col4:
        st.metric(
            "동물계 데이터 비율",
            f"{len(animal_df) / len(original_df) * 100:.1f}%"
        )

    st.divider()

    st.subheader("1. 데이터 컬럼 설명")

    column_info = []

    for col in original_df.columns:
        column_info.append({
            "컬럼 이름": col,
            "우리말 의미": COLUMN_LABELS.get(col, col),
            "설명": COLUMN_DESCRIPTIONS.get(col, "설명 없음"),
            "데이터 유형": get_type_name(original_df[col])
        })

    column_info_df = pd.DataFrame(column_info)

    st.dataframe(
        column_info_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("2. 컬럼별 결측치 확인")

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

    st.info(
        "결측치는 데이터가 비어 있는 상태를 의미합니다. "
        "결측치가 있다고 해서 모든 행을 삭제할 필요는 없으며, "
        "분석 목적에 따라 처리 방법을 결정해야 합니다."
    )

    st.divider()

    st.subheader("3. 원본 데이터 미리 보기")

    st.dataframe(
        original_df.head(10),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 11. 데이터 전처리 화면
# =========================================================

elif page == "🧹 데이터 전처리":

    st.header("🧹 데이터 전처리")

    st.write(
        "전체 생물 데이터에서 동물계에 해당하는 자료를 추출하고, "
        "멸종 위험 등급을 분석 목적에 맞게 구분합니다."
    )

    st.subheader("1. 전처리 전후 데이터 수")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "원본 데이터",
            format_number(len(original_df))
        )

    with col2:
        st.metric(
            "동물계 데이터",
            format_number(len(animal_df))
        )

    with col3:
        st.metric(
            "중복 제거 후",
            format_number(len(animal_no_duplicates)),
            delta=f"-{removed_duplicate_count:,}개",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "최종 분석 데이터",
            format_number(len(preprocessed_df))
        )

    st.divider()

    st.subheader("2. 동물계 데이터 추출")

    non_animal_count = len(original_df) - len(animal_df)

    st.write(
        f"- 원본 데이터: {len(original_df):,}개"
    )
    st.write(
        f"- 동물계 데이터: {len(animal_df):,}개"
    )
    st.write(
        f"- 동물계 이외의 데이터: {non_animal_count:,}개"
    )

    kingdom_counts = (
        original_df["kingdom_name"]
        .value_counts()
        .rename_axis("생물계")
        .reset_index(name="데이터 수")
    )

    kingdom_counts["생물계"] = kingdom_counts["생물계"].replace({
        "ANIMALIA": "동물계",
        "PLANTAE": "식물계",
        "FUNGI": "균계",
        "CHROMISTA": "크로미스타계"
    })

    fig_kingdom = px.bar(
        kingdom_counts,
        x="생물계",
        y="데이터 수",
        text="데이터 수",
        title="생물계별 데이터 수",
        labels={
            "생물계": "생물 분류",
            "데이터 수": "데이터 개수"
        }
    )

    fig_kingdom.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_kingdom.update_layout(
        yaxis_title="데이터 개수",
        xaxis_title="생물 분류"
    )

    st.plotly_chart(
        fig_kingdom,
        use_container_width=True
    )

    st.divider()

    st.subheader("3. 중복 데이터 확인")

    duplicate_col1, duplicate_col2, duplicate_col3 = st.columns(3)

    with duplicate_col1:
        st.metric(
            "완전히 동일한 행",
            format_number(exact_duplicate_count)
        )

    with duplicate_col2:
        st.metric(
            "중복된 고유 번호",
            format_number(taxonid_duplicate_count)
        )

    with duplicate_col3:
        st.metric(
            "반복된 학명",
            format_number(scientific_name_duplicate_count)
        )

    st.caption(
        "반복된 학명은 같은 학명이 여러 행에 나타난 횟수입니다. "
        "동일한 생물종이라고 단정하지 않고, 고유 식별 번호(taxonid)를 "
        "기준으로 중복을 제거했습니다."
    )

    st.write(
        f"고유 번호 중복 제거로 제외된 데이터: "
        f"**{removed_duplicate_count:,}개**"
    )

    st.divider()

    st.subheader("4. 멸종 위험 등급 확인")

    category_table = make_category_table(animal_no_duplicates)

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "LC, NT, VU, EN, CR은 현재 주요 위험 등급이며, "
        "DD, EX, EW 및 과거 등급은 별도로 구분합니다."
    )

    st.divider()

    st.subheader("5. 전처리 과정에서 제외된 데이터")

    exclusion_table = pd.DataFrame([
        {
            "제외 이유": "정보부족(DD)",
            "제외 데이터 수": dd_count
        },
        {
            "제외 이유": "절멸(EX)",
            "제외 데이터 수": ex_count
        },
        {
            "제외 이유": "야생절멸(EW)",
            "제외 데이터 수": ew_count
        },
        {
            "제외 이유": "과거 등급(LR/lc, LR/nt, LR/cd)",
            "제외 데이터 수": historical_count
        },
        {
            "제외 이유": "등급 정보 없음",
            "제외 데이터 수": missing_category_count
        },
        {
            "제외 이유": "기타 등급 또는 분류되지 않은 값",
            "제외 데이터 수": other_category_count
        }
    ])

    st.dataframe(
        exclusion_table,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "DD는 멸종 위험을 판단할 정보가 부족한 상태이며, "
        "EX와 EW는 이미 절멸했거나 야생에서 절멸한 상태입니다. "
        "이들은 현재 위험 등급 예측 대상에서 제외했습니다. "
        "과거 등급도 현재 등급과 임의로 합치지 않았습니다."
    )

    st.divider()

    st.subheader("6. 최종 분석 데이터")

    st.write(
        f"최종적으로 현재 주요 위험 등급 "
        f"(LC, NT, VU, EN, CR)에 해당하는 "
        f"**{len(preprocessed_df):,}개 데이터**를 생성했습니다."
    )

    st.dataframe(
        preprocessed_df[
            [
                "taxonid",
                "scientific_name",
                "main_common_name",
                "class_name",
                "order_name",
                "family_name",
                "category",
                "멸종 위험 등급"
            ]
        ].head(10),
        use_container_width=True,
        hide_index=True
    )

    csv_bytes = preprocessed_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="전처리된 동물 데이터 CSV 다운로드",
        data=csv_bytes,
        file_name="전처리된_멸종위기동물.csv",
        mime="text/csv"
    )

    st.caption(
        "원본 데이터는 변경하지 않았으며, "
        "전처리 결과는 별도의 데이터로 생성했습니다."
    )


# =========================================================
# 12. 데이터 탐색 화면
# =========================================================

elif page == "📊 데이터 탐색":

    st.header("📊 데이터 탐색")

    st.write(
        "동물계 데이터의 멸종 위험 등급 분포와 "
        "생물의 분류 단계에 따른 위험 등급의 차이를 살펴봅니다."
    )

    if preprocessed_df.empty:
        st.warning(
            "분석할 데이터가 없습니다. CSV 파일의 멸종 위험 등급을 확인해 주세요."
        )
        st.stop()

    # -----------------------------------------------------
    # 12-1. 멸종 위험 등급별 동물 수
    # -----------------------------------------------------

    st.subheader("1. 멸종 위험 등급별 동물 수")

    risk_counts = (
        preprocessed_df["category"]
        .value_counts()
        .reindex(CURRENT_RISK_ORDER, fill_value=0)
        .rename_axis("등급 코드")
        .reset_index(name="동물 수")
    )

    risk_counts["멸종 위험 등급"] = (
        risk_counts["등급 코드"]
        .map(CURRENT_RISK_LABELS)
    )

    fig_count = px.bar(
        risk_counts,
        x="멸종 위험 등급",
        y="동물 수",
        text="동물 수",
        category_orders={
            "멸종 위험 등급": [
                "관심대상",
                "준위협",
                "취약",
                "위기",
                "위급"
            ]
        },
        title="멸종 위험 등급별 동물 수",
        labels={
            "멸종 위험 등급": "멸종 위험 등급",
            "동물 수": "동물 개수"
        }
    )

    fig_count.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_count.update_layout(
        xaxis_title="멸종 위험 등급",
        yaxis_title="동물 개수"
    )

    st.plotly_chart(
        fig_count,
        use_container_width=True
    )

    st.dataframe(
        risk_counts[
            ["등급 코드", "멸종 위험 등급", "동물 수"]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------------------------------
    # 12-2. 멸종 위험 등급별 비율
    # -----------------------------------------------------

    st.subheader("2. 멸종 위험 등급별 비율")

    risk_ratio = risk_counts.copy()

    risk_ratio["비율(%)"] = (
        risk_ratio["동물 수"]
        / risk_ratio["동물 수"].sum()
        * 100
    ).round(2)

    fig_ratio = px.pie(
        risk_ratio,
        names="멸종 위험 등급",
        values="동물 수",
        hole=0.4,
        title="멸종 위험 등급별 비율",
        category_orders={
            "멸종 위험 등급": [
                "관심대상",
                "준위협",
                "취약",
                "위기",
                "위급"
            ]
        }
    )

    fig_ratio.update_traces(
        textposition="inside",
        textinfo="label+percent"
    )

    st.plotly_chart(
        fig_ratio,
        use_container_width=True
    )

    st.dataframe(
        risk_ratio[
            ["멸종 위험 등급", "동물 수", "비율(%)"]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------------------------------
    # 12-3. 강별 위험 등급 분포
    # -----------------------------------------------------

    st.subheader("3. 생물의 강(class)에 따른 멸종 위험 등급")

    class_graph, class_counts, class_percent = make_group_analysis(
        preprocessed_df,
        "class_name",
        "강"
    )

    fig_class = px.bar(
        class_graph,
        x="표시 분류",
        y="동물 수",
        color="등급 이름",
        barmode="stack",
        title="강별 멸종 위험 등급 분포",
        labels={
            "표시 분류": "생물의 강",
            "동물 수": "동물 개수",
            "등급 이름": "멸종 위험 등급"
        }
    )

    fig_class.update_layout(
        xaxis_title="생물의 강",
        yaxis_title="동물 개수",
        legend_title="멸종 위험 등급"
    )

    st.plotly_chart(
        fig_class,
        use_container_width=True
    )

    st.markdown("**강별 등급 개수**")
    st.dataframe(
        class_counts,
        use_container_width=True
    )

    st.markdown("**강별 등급 비율(%)**")
    st.dataframe(
        class_percent,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # 12-4. 목별 위험 등급 분포
    # -----------------------------------------------------

    st.subheader("4. 생물의 목(order)에 따른 멸종 위험 등급")

    order_graph, order_counts, order_percent = make_group_analysis(
        preprocessed_df,
        "order_name",
        "목"
    )

    fig_order = px.bar(
        order_graph,
        x="표시 분류",
        y="동물 수",
        color="등급 이름",
        barmode="stack",
        title="목별 멸종 위험 등급 분포",
        labels={
            "표시 분류": "생물의 목",
            "동물 수": "동물 개수",
            "등급 이름": "멸종 위험 등급"
        }
    )

    fig_order.update_layout(
        xaxis_title="생물의 목",
        yaxis_title="동물 개수",
        legend_title="멸종 위험 등급"
    )

    st.plotly_chart(
        fig_order,
        use_container_width=True
    )

    st.markdown("**목별 등급 개수**")
    st.dataframe(
        order_counts,
        use_container_width=True
    )

    st.markdown("**목별 등급 비율(%)**")
    st.dataframe(
        order_percent,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # 12-5. 과별 위험 등급 분포
    # -----------------------------------------------------

    st.subheader("5. 생물의 과(family)에 따른 멸종 위험 등급")

    family_graph, family_counts, family_percent = make_group_analysis(
        preprocessed_df,
        "family_name",
        "과"
    )

    fig_family = px.bar(
        family_graph,
        x="표시 분류",
        y="동물 수",
        color="등급 이름",
        barmode="stack",
        title="과별 멸종 위험 등급 분포",
        labels={
            "표시 분류": "생물의 과",
            "동물 수": "동물 개수",
            "등급 이름": "멸종 위험 등급"
        }
    )

    fig_family.update_layout(
        xaxis_title="생물의 과",
        yaxis_title="동물 개수",
        legend_title="멸종 위험 등급"
    )

    st.plotly_chart(
        fig_family,
        use_container_width=True
    )

    st.markdown("**과별 등급 개수**")
    st.dataframe(
        family_counts,
        use_container_width=True
    )

    st.markdown("**과별 등급 비율(%)**")
    st.dataframe(
        family_percent,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # 12-6. 탐색 결과 안내
    # -----------------------------------------------------

    st.subheader("6. 탐색 결과 해석하기")

    st.write(
        "위 그래프와 표를 통해 생물의 강, 목, 과에 따라 "
        "멸종 위험 등급의 분포가 어떻게 나타나는지 비교할 수 있습니다."
    )

    st.info(
        "그래프에 표시된 '기타'는 해당 분류 단계에서 "
        "데이터 수가 많은 상위 15개 분류에 포함되지 않은 "
        "나머지 분류를 합친 것입니다. "
        "따라서 기타에 속한 분류는 개별적으로 확인해야 합니다."
    )

    st.warning(
        "이 분석은 분류학적 특성과 멸종 위험 등급 사이의 "
        "분포 관계를 살펴보는 것입니다. "
        "특정 분류에 속한다는 사실만으로 멸종 위험의 원인을 "
        "단정할 수는 없습니다."
    )


# =========================================================
# 13. 화면 하단 안내
# =========================================================

st.sidebar.divider()
st.sidebar.caption(
    "멸종 위기 동물 데이터 탐색실\n"
    "데이터 분석 및 학습을 위한 앱입니다."
)

st.caption(
    "본 앱은 데이터 탐색과 학습을 위한 도구이며, "
    "멸종 위험의 원인이나 보호 우선순위를 확정하는 전문 평가를 대신하지 않습니다."
)
