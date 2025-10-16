import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Mini Timetable Scheduler", page_icon="📘", layout="centered")

st.title("📘 Mini Timetable Scheduler")
st.markdown("**산업공학의 스케줄링 원리를 간단히 체험해보는 시간표 자동 생성기**")

# --- 사용자 입력 영역 ---
st.sidebar.header("🧩 시간표 조건 설정")

# 요일, 교시, 과목 입력
days = st.sidebar.multiselect("요일 선택", ["월", "화", "수", "목", "금"], default=["월", "화", "수", "목", "금"])
num_periods = st.sidebar.slider("하루 교시 수 선택", 3, 8, 6)
subjects_input = st.sidebar.text_area("과목 입력 (쉼표로 구분)", "국어, 수학, 영어, 과학, 사회, 체육, 예체능")

subjects = [s.strip() for s in subjects_input.split(",") if s.strip() != ""]

if not subjects:
    st.warning("⚠️ 과목을 최소 한 개 이상 입력해주세요.")
    st.stop()

# 시수 제한 설정
st.sidebar.subheader("⏱️ 시수(과목별 주당 최대 수업 횟수)")
max_hours = {}
for subject in subjects:
    max_hours[subject] = st.sidebar.number_input(f"{subject}", min_value=1, max_value=10, value=3, step=1)

st.sidebar.markdown("---")

if st.button("🗓️ 시간표 생성하기"):
    total_slots = len(days) * num_periods

    # 시수 제한 내에서 가능한 과목 리스트 생성
    subject_pool = []
    for subject, limit in max_hours.items():
        subject_pool.extend([subject] * limit)

    if len(subject_pool) < total_slots:
        st.warning("⚠️ 시수 합이 전체 시간표 칸 수보다 적습니다. 시수를 늘려주세요.")
        st.stop()

    # 시간표 생성
    timetable = []
    for day in days:
        daily_subjects = []
        for _ in range(num_periods):
            available = [s for s in subjects if s not in daily_subjects[-1:]]  # 같은 과목 연속 방지
            choice = random.choice(available)
            daily_subjects.append(choice)
        timetable.append(daily_subjects)

    # DataFrame으로 변환 + 교시 번호 추가
    df = pd.DataFrame(timetable, index=days, columns=[f"{i+1}교시" for i in range(num_periods)]).T
    df.index.name = "교시"
    df.reset_index(inplace=True)

    st.success("✅ 시간표 생성 완료!")
    st.markdown("### 📅 생성된 시간표")
    st.dataframe(df, use_container_width=True)

    # 표 아래 간단한 분석
    st.markdown("---")
    st.markdown("### 📊 간단한 분석")
    subject_counts = {s: sum(df[col].value_counts().get(s, 0) for col in df.columns if col != '교시') for s in subjects}
    st.write(pd.DataFrame(list(subject_counts.items()), columns=["과목", "총 시수"]).set_index("과목"))

    st.info("""
    💡 이 시간표 생성 과정은 산업공학의 **스케줄링 문제**를 단순화한 형태입니다.  
    실제 산업공학에서는 제약 조건(시간, 자원, 비용 등)을 고려해  
    '최적화 알고리즘'으로 더 효율적인 배치를 찾습니다.
    """)

else:
    st.info("🧩 왼쪽 사이드바에서 조건을 설정하고 **‘시간표 생성하기’** 버튼을 눌러보세요.")

