import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Mini Timetable Scheduler", page_icon="📘", layout="centered")

st.title("📘 Mini Timetable Scheduler")
st.markdown("**산업공학의 스케줄링 원리를 간단히 체험해보는 시간표 자동 생성기**")

# --- 사용자 입력 ---
st.sidebar.header("🧩 시간표 조건 설정")

days = st.sidebar.multiselect("요일 선택", ["월", "화", "수", "목", "금"], default=["월", "화", "수", "목", "금"])
num_periods = st.sidebar.slider("하루 교시 수 선택", 3, 8, 6)
subjects_input = st.sidebar.text_area("과목 입력 (쉼표로 구분)", "국어, 수학, 영어, 과학, 사회, 체육, 예체능")

subjects = [s.strip() for s in subjects_input.split(",") if s.strip() != ""]

if not subjects:
    st.warning("⚠️ 과목을 최소 한 개 이상 입력해주세요.")
    st.stop()

# 시수 제한 입력
st.sidebar.subheader("⏱️ 시수(과목별 주당 최대 수업 횟수)")
max_hours = {}
for subject in subjects:
    max_hours[subject] = st.sidebar.number_input(f"{subject}", min_value=1, max_value=10, value=3, step=1)

st.sidebar.markdown("---")

if st.button("🗓️ 시간표 생성하기"):
    total_slots = len(days) * num_periods
    total_hours = sum(max_hours.values())

    # 남은 시수 초기화
    remaining_hours = max_hours.copy()

    # 전체 슬롯 리스트 생성 (요일 * 교시)
    slots = [(day, period) for day in days for period in range(num_periods)]

    # 전체 시간표 딕셔너리 초기화
    timetable = {day: ["공강"] * num_periods for day in days}

    # --- 전체 단위 배정 알고리즘 ---
    # 1️⃣ 과목 리스트를 시수만큼 확장 (예: 수학*3, 영어*2 ...)
    subject_pool = []
    for subj, cnt in max_hours.items():
        subject_pool.extend([subj] * cnt)

    # 2️⃣ 랜덤 섞기 (배정 순서 다양화)
    random.shuffle(subject_pool)

    # 3️⃣ 과목 하나씩 배정
    for subj in subject_pool:
        # 가능한 위치 후보: 공강이며, 앞뒤가 같은 과목이 아닌 슬롯
        possible_slots = []
        for day in days:
            for p in range(num_periods):
                if timetable[day][p] == "공강":
                    prev_subj = timetable[day][p - 1] if p > 0 else None
                    next_subj = timetable[day][p + 1] if p < num_periods - 1 else None
                    if subj != prev_subj and subj != next_subj:
                        possible_slots.append((day, p))
        # 공강 최소화: 이미 수업이 있는 구간 근처를 우선 배정
        if possible_slots:
            # 요일별로 공강 중앙보단 양끝 피하기
            possible_slots.sort(key=lambda x: abs(x[1] - num_periods / 2))
            day, p = possible_slots[0]
            timetable[day][p] = subj
            remaining_hours[subj] -= 1

    # --- DataFrame 변환 ---
    df = pd.DataFrame(timetable, index=[f"{i+1}교시" for i in range(num_periods)])
    df.index.name = "교시"
    df.reset_index(inplace=True)

    st.success("✅ 시간표 생성 완료!")
    st.markdown("### 📅 생성된 시간표")
    st.dataframe(df, use_container_width=True)

    # --- 통계 분석 ---
    st.markdown("---")
    st.markdown("### 📊 과목별 실제 배정 시수 및 공강 수")
    subject_counts = {s: sum(df[col].value_counts().get(s, 0) for col in df.columns if col != '교시') for s in subjects}
    total_free = sum(df[col].value_counts().get("공강", 0) for col in df.columns if col != '교시')

    stats_df = pd.DataFrame(list(subject_counts.items()), columns=["과목", "실제 배정 시수"]).set_index("과목")
    st.write(stats_df)
    st.info(f"🕳️ 전체 공강 수: **{total_free}칸**")

    # --- 산업공학 연결 ---
    st.markdown("---")
    st.markdown("### 🧠 산업공학적 의미")
    st.write("""
    이 시간표 생성은 실제 산업공학의 **스케줄링(Scheduling)** 문제를 단순화한 모델이에요.  
    여기서 시수 제한과 공강 최소화는 **자원 제약 하의 효율적 배치 문제(Resource-Constrained Optimization)** 와 대응됩니다.

    산업공학에서는 이런 문제를 해결할 때 다음과 같은 접근법을 사용합니다:
    - **정수계획법(Integer Programming)** : 제약 조건을 수식으로 정의하고 최적해를 계산
    - **휴리스틱(Heuristic) 알고리즘** : 지금처럼 간단한 규칙 기반으로 빠르게 근사해 찾기
    - **유전 알고리즘(Genetic Algorithm)** : 가능한 시간표를 '진화'시켜 최적화

    즉, 이 코드는 단순히 랜덤이 아니라 산업공학의 사고방식 —  
    "**제약을 고려하며 효율을 극대화하는 설계**" — 를 담고 있어요.
    """)

else:
    st.info("🧩 왼쪽 사이드바에서 조건을 설정하고 **‘시간표 생성하기’** 버튼을 눌러보세요.")
