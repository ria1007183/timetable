import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Mini Timetable Scheduler", page_icon="📘", layout="centered")

st.title("📘 Mini Timetable Scheduler")
st.markdown("**산업공학의 스케줄링 원리를 체험해보는 간단한 시간표 자동 생성기**")

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

    if total_hours < total_slots:
        st.info("💡 시수 합이 전체 칸보다 적으므로 일부 공강이 생길 수 있습니다.")
    elif total_hours > total_slots:
        st.warning("⚠️ 시수 합이 전체 칸보다 많습니다. 일부 시수는 무시됩니다.")

    # --- 스케줄링 시작 ---
    remaining_hours = max_hours.copy()
    timetable = []

    for day in days:
        daily_subjects = []
        for period in range(num_periods):
            # 공강 최소화를 위해 앞뒤 교시에 이미 수업이 있으면 가능하면 공강 피하기
            previous = daily_subjects[-1] if daily_subjects else None
            # 남은 시수가 있는 과목 중 연속수업 방지
            available = [s for s in subjects if remaining_hours[s] > 0 and s != previous]

            if not available:
                available = [s for s in subjects if remaining_hours[s] > 0]

            if not available:
                # 공강 배치하되, 가능한 중앙보다는 양끝(시작이나 끝)에 배정
                if period == 0 or period == num_periods - 1:
                    daily_subjects.append("공강")
                else:
                    # 공강 최소화를 위해 50% 확률로 이전 과목을 연속 허용
                    if previous and random.random() < 0.5:
                        daily_subjects.append(previous)
                    else:
                        daily_subjects.append("공강")
            else:
                choice = random.choice(available)
                daily_subjects.append(choice)
                remaining_hours[choice] -= 1
        timetable.append(daily_subjects)

    # --- DataFrame으로 변환 ---
    df = pd.DataFrame(timetable, index=days, columns=[f"{i+1}교시" for i in range(num_periods)]).T
    df.index.name = "교시"
    df.reset_index(inplace=True)

    st.success("✅ 시간표 생성 완료!")
    st.markdown("### 📅 생성된 시간표")
    st.dataframe(df, use_container_width=True)

    # --- 공강 개수 분석 ---
    st.markdown("---")
    st.markdown("### 📊 과목별 실제 배정 시수 & 공강 분석")
    subject_counts = {s: sum(df[col].value_counts().get(s, 0) for col in df.columns if col != '교시') for s in subjects}
    total_free = sum(df[col].value_counts().get("공강", 0) for col in df.columns if col != '교시')

    stats_df = pd.DataFrame(list(subject_counts.items()), columns=["과목", "실제 배정 시수"]).set_index("과목")
    st.write(stats_df)
    st.info(f"🕳️ 전체 공강 수: **{total_free}칸**")

    # --- 산업공학적 연결 ---
    st.markdown("---")
    st.markdown("### 🧠 산업공학적 시사점")
    st.write("""
    이 시간표 생성은 실제 산업공학의 **스케줄링(Scheduling)** 문제를 단순화한 모델입니다.  
    여기서 공강 최소화는 **효율성 최적화(Efficiency Optimization)** 문제로 해석할 수 있습니다.

    산업공학에서는 이런 문제를 해결하기 위해 다음과 같은 기법들을 사용합니다:
    - **정수계획법(Integer Programming)**
    - **유전 알고리즘(Genetic Algorithm)**
    - **시뮬레이티드 어닐링(Simulated Annealing)**
    
    즉, 지금의 단순 규칙 기반 로직은 ‘산업공학의 사고방식’을 체험하기 위한
    아주 작은 모델 버전이에요 💡
    """)

else:
    st.info("🧩 왼쪽 사이드바에서 조건을 설정하고 **‘시간표 생성하기’** 버튼을 눌러보세요.")
