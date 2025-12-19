import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os

from db.database import init_db
from ai.clustering import assign_cluster as ai_assign_cluster
from ai.analytics import analyze_patterns, goal_prediction

# ---------- CONFIG ----------
st.set_page_config("AI Learning Engine", layout="wide")

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- DATABASE ----------
conn = init_db()

# ---------- AUTH ----------
def auth_ui():
    st.title("🎓 AI Learning Engine")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, password)
            ).fetchone()
            if user:
                st.session_state.user = user
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Name")
        email = st.text_input("Email ")
        password = st.text_input("Password ", type="password")
        interests = st.text_input("Interests (e.g. ML, Math)")
        pref = st.selectbox("Preferred Format", ["Video", "Text", "Discussion"])

        if st.button("Create Account"):
            try:
                conn.execute(
                    "INSERT INTO users (name, email, password) VALUES (?,?,?)",
                    (name, email, password)
                )
                uid = conn.execute(
                    "SELECT user_id FROM users WHERE email=?", (email,)
                ).fetchone()[0]

                conn.execute(
                    "INSERT INTO student_profile VALUES (?,?,?)",
                    (uid, interests, pref)
                )
                conn.commit()
                st.success("Account created. Login now.")
            except:
                st.error("Email already exists")

if st.session_state.user is None:
    auth_ui()
    st.stop()

user_id = st.session_state.user[0]

# ---------- BASELINE DATA ----------
@st.cache_data
def load_baseline():
    df = pd.read_csv("data/Student_Performance.csv")
    return df[['math score', 'reading score']].rename(columns={'math score': 'math', 'reading score': 'reading'})

baseline = load_baseline()

# ---------- CLUSTER ----------

# ---------- SIDEBAR ----------
st.sidebar.header("📝 New Assessment")
m = st.sidebar.number_input("Math Score", 0, 100, 70)
r = st.sidebar.number_input("Reading Score", 0, 100, 65)
c = st.sidebar.slider("Engagement (Clicks)", 0, 1000, 300)

if st.sidebar.button("Save Progress"):
    cluster = ai_assign_cluster(baseline, m, r)
    conn.execute("""
        INSERT INTO progress
        (user_id, date, topic, math, reading, clicks, cluster)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, datetime.now().strftime("%Y-%m-%d %H:%M"),
          "General", m, r, c, cluster))
    conn.commit()
    st.success("Progress saved!")

# ---------- LOAD USER HISTORY ----------
history = pd.read_sql_query(
    "SELECT * FROM progress WHERE user_id=?",
    conn,
    params=(user_id,)
)

current_cluster = ai_assign_cluster(baseline, m, r)

# ---------- DASHBOARD ----------
st.title("📊 Student Dashboard")

col1, col2 = st.columns([2,1])

with col1:
    fig = px.scatter(
        baseline, x="math", y="reading",
        opacity=0.2, template="plotly_dark"
    )
    fig.add_scatter(
        x=[m], y=[r],
        mode="markers",
        marker=dict(size=20, color="red"),
        name="You"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Current Cluster", current_cluster)
    st.metric("Engagement", c)

# ---------- TIMELINE ----------
if not history.empty:
    st.subheader("📈 Progress Over Time")
    st.line_chart(history.set_index("date")[["math", "reading"]])

    # ---------- ANALYTICS ----------
    st.subheader("🔍 Performance Analysis")
    msg, velocity, recent = analyze_patterns(history)
    st.write(msg)
    if velocity > 0:
        target = 90  # example target
        sessions = goal_prediction(recent, velocity, target)
        if sessions:
            st.info(f"To reach {target} points, you need about {sessions} more sessions at this rate.")

# ---------- PROFILE ----------
profile = conn.execute(
    "SELECT interests, preferred_format FROM student_profile WHERE user_id=?",
    (user_id,)
).fetchone()

st.subheader("👤 Student Profile")
st.write(f"**Interests:** {profile[0]}")
st.write(f"**Preferred Format:** {profile[1]}")

# ---------- RESOURCES ----------
resource_map = {
    0: [
        ("Khan Academy Basics", "https://www.khanacademy.org"),
        ("Math Antics", "https://mathantics.com")
    ],
    1: [
        ("Brilliant Practice", "https://brilliant.org"),
        ("IXL", "https://www.ixl.com")
    ],
    2: [
        ("MIT OpenCourseWare", "https://ocw.mit.edu"),
        ("Wolfram Alpha", "https://www.wolframalpha.com")
    ]
}

st.subheader("📚 Recommended Resources")
for title, link in resource_map[current_cluster]:
    st.link_button(title, link, use_container_width=True)

if c < 200:
    st.warning("Low engagement detected — try one short video today!")
