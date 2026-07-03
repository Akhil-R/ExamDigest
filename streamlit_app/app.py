# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import requests

# Base URL of the FastAPI backend server
BACKEND_URL = st.sidebar.text_input("Backend API URL", "http://localhost:8000")

st.set_page_config(
    page_title="Current Affairs Digest Agent",
    page_icon="📰",
    layout="wide"
)

# Header Section
st.title("📰 Current Affairs Digest Agent")
st.markdown("""
Welcome to the **Current Affairs Digest Agent** for competitive exam aspirants.
Select your target exam and generate a tailored study digest and practice quiz curated from syllabus-relevant news.
""")

# Exam selection
exam_type = st.selectbox(
    "Select your target exam:",
    options=["psc", "ssc", "railway"],
    format_func=lambda x: x.upper()
)

# Generate button
generate_button = st.button("🚀 Generate Digest & Quiz", type="primary")

# Initialize session state for tracking data
if "digest_data" not in st.session_state:
    st.session_state["digest_data"] = None
if "quiz_data" not in st.session_state:
    st.session_state["quiz_data"] = None

if generate_button:
    with st.spinner("Executing staged agent workflow..."):
        try:
            # 1. Fetch current affairs
            digest_res = requests.get(f"{BACKEND_URL}/current-affairs", params={"exam": exam_type})
            if digest_res.status_code == 200:
                st.session_state["digest_data"] = digest_res.json().get("digest", [])
            else:
                st.error(f"Failed to fetch digest: {digest_res.text}")
                st.session_state["digest_data"] = None
                
            # 2. Fetch quiz
            quiz_res = requests.get(f"{BACKEND_URL}/quiz", params={"exam": exam_type})
            if quiz_res.status_code == 200:
                st.session_state["quiz_data"] = quiz_res.json().get("quiz", [])
            else:
                st.error(f"Failed to fetch quiz: {quiz_res.text}")
                st.session_state["quiz_data"] = None
                
            if st.session_state["digest_data"] and st.session_state["quiz_data"]:
                st.success("Successfully generated digest and quiz!")
        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the FastAPI backend at {BACKEND_URL}. "
                "Please make sure the server is running by executing: "
                "`uvicorn server.app:app --host 127.0.0.1 --port 8000`"
            )

# Show results if we have data in session state
if st.session_state["digest_data"] is not None:
    tab1, tab2 = st.tabs(["📖 Study Digest", "✍️ Practice Quiz"])
    
    with tab1:
        st.subheader(f"Exam Facts for {exam_type.upper()}")
        
        # Display digest items
        for i, item in enumerate(st.session_state["digest_data"], 1):
            with st.container():
                st.markdown(f"### Fact {i}: {item['title']}")
                st.markdown(f"**Description:** {item['fact']}")
                st.markdown(f"🔗 [Source Article]({item['source_url']})")
                st.markdown(f"🏷️ **Tags:** " + ", ".join([f"`{tag}`" for tag in item['tags']]))
                st.divider()
                
    with tab2:
        st.subheader("Practice Questions")
        st.markdown("Test your retention with these multiple-choice questions based on the digest.")
        
        quiz_items = st.session_state["quiz_data"]
        
        for index, q in enumerate(quiz_items):
            st.markdown(f"#### Q{index+1}: {q['question']}")
            
            # Interactive options selection
            user_choice = st.radio(
                f"Select an option for Q{index+1}:",
                options=q["options"],
                key=f"q_{index}_{q['id']}"
            )
            
            # Reveal answer & explanation
            with st.expander(f"Reveal Answer for Q{index+1}"):
                st.markdown(f"**Correct Answer:** {q['correct_answer']}")
                st.markdown(f"**Explanation:** {q['explanation']}")
                
                # Check if choice is correct
                if user_choice == q["correct_answer"]:
                    st.success("Correct Answer! 🎉")
                else:
                    st.info("Study the explanation to learn more.")
            st.divider()
else:
    st.info("Select an exam category and click the button above to begin.")
