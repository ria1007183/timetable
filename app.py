import streamlit as st
import random

st.title("🧠 나만의 시간표 자동 생성기 (Mini Scheduler)")

# 1️⃣ 사용자 입력
subjects_input = st.text_input("과목을 콤마로 구분해 입력하세요 (예: 국어,수학,영어)", "국어,수학,영어")
days = st.number_input("요일 수를 입력하세요", min_value=1, max_value=7, value=3)
periods = st.number_input("하루 교시 수를 입력하세요", min_value=1, max_value=10, value=3)

subjects = [s.strip() for s in subjects_input.split(",")]

st.subheader("📘 각 과목의 주당 수업 횟수 입력")
hours_per_subject = {}
for s in subjects:
    hours_per_subject[s] = st.number_input(f"{s} 시수", min_value=1, max_value=10, value=2, key=s)

# 2️⃣ 시간표 생성 함수
def make_schedule(subjects, hours_per_subject, days, periods):
    total_slots = days * periods
    classes = []
    for subject, hours in hours_per_subject.items():
        classes += [subject] * hours
    while len(classes) < total_slots:
        classes.append(random.choice(subjects))
    random.shuffle(classes)
    schedule = [[None for _ in range(periods)] for _ in range(days)]
    idx = 0
    for i in range(days):
        for j in range(periods):
            schedule[i][j] = classes[idx]
            idx += 1
    return schedule

def valid(schedule):
    for i in range(len(schedule)):
        for j in range(len(schedule[0]) - 1):
            if schedule[i][j] == schedule[i][j + 1]:
                return False
    return True

# 3️⃣ 버튼 클릭 시 시간표 생성
if st.button("⏰ 시간표 생성하기"):
    schedule = make_schedule(subjects, hours_per_subject, days, periods)
    while not valid(schedule):
        schedule = make_schedule(subjects, hours_per_subject, days, periods)

    st.success("✅ 시간표 생성 완료!")
    st.write("📅 **결과:**")
    st.table([[schedule[d][p] for d in range(days)] for p in range(periods)])
