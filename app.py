import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import fitz  # PyMuPDF
from datetime import date

# Load API key
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# USERS FILE SETUP
# =========================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()
# st.write(users)
# st.write("DEBUG USERS:", users)

# =========================
# SIGNUP FUNCTION
# =========================
def signup(username, password):
    if username in users:
        return False, "Username already exists"

    users[username] = {
    "password": password,
    "plan": "free",
    "usage_count": 0,
    "last_used": str(date.today())


}
    save_users(users)
    return True, "Account created successfully"

# =========================
# LOGIN FUNCTION
# =========================
def login_user(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# =========================
# AUTH PAGE (LOGIN + SIGNUP)
# =========================
def auth_page():
    st.title("🔐 Zyphora AI Login System")

    option = st.radio("Choose Option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        if st.button("Create Account"):
            ok, msg = signup(username, password)
            if ok:
             st.session_state["logged_in"] = True
             st.session_state["username"] = username
             st.success("Account created successfully 🚀")
             st.rerun()
            else:
                st.error(msg)
                
    if option == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login Successful 🚀")
                st.rerun()
            else:
                st.error("Invalid username or password")

# =========================
# LOGIN PROTECTION
# =========================

if not st.session_state["logged_in"]:
    auth_page()
    st.stop()

# Current user
username = st.session_state["username"]

today = str(date.today())

if users[username]["last_used"] != today:
    users[username]["usage_count"] = 0
    users[username]["last_used"] = today
    save_users(users)

if users[username]["plan"] == "free":
    if users[username]["usage_count"] >= 3:
        st.error("🚫 Daily limit reached. Upgrade to Pro or Premium.")
        st.stop()

# Temporary plan
# Temporary plan
user_plan = users[username].get("plan", "free")

# Sidebar User Info
st.sidebar.title("🚀 Zyphora AI")
st.sidebar.success(f"👤 {username}")
st.sidebar.info(f"💎 Plan: {user_plan.upper()}")

if user_plan == "free":
    remaining = 3 - users[username]["usage_count"]
    st.sidebar.warning(
        f"📊 Remaining Uses Today: {remaining}"
    )

# ADD THIS HERE 👇
page = st.sidebar.radio(
    "Menu",
    ["Resume Analyzer", "Pricing"]
)

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""

    pdf = fitz.open(stream=uploaded_file.read(),
                    filetype="pdf")

    for page in pdf:
        text += page.get_text()

    return text

# AI Analysis
def analyze_resume(text,job_description):

    prompt = f"""
You are an expert HR Recruiter, ATS Specialist, Career Coach, and Learning Mentor.

Analyze the resume and provide a professional report.

IMPORTANT RULES:
1. ATS Score must be ONLY out of 100.
2. Use Markdown headings (#) for all section titles.
3. Use bullet points for lists.
4. Be specific and personalized to the resume.
5. Do NOT give generic answers.
6. Recommend realistic career paths.
7. Learning Roadmap must be detailed and actionable.
8. Extract ATS keywords from Job Description.
9. Compare Resume vs Job Description.
10. Show missing ATS keywords separately.
11. Explain why those keywords matter.
12. Do not limit skills extraction.

Return the response in this exact format:

# ATS Score

ATS Score: X/100
Brief explanation of the score.

# ATS Breakdown
Resume Format: X/10
Keywords: X/20
Skills: X/20
Projects: X/20
Experience: X/15
Education: X/15

Brief explanation of the score.

# Skills

Extract EVERY skill found in the resume.

Group them into categories:

## Programming Languages
- ...

## Data Analysis Tools
- ...

## Libraries & Frameworks
- ...

## Databases
- ...

## Visualization Tools
- ...

## Soft Skills
- ...

Do NOT limit the number of skills.
Show every skill found in the resume.
Example:
Programming Languages
- Python
- SQL

Data Analysis
- Pandas
- NumPy

Visualization
- Power BI
- Matplotlib

Machine Learning
- Scikit-learn

Business Tools
- Excel
- Tally

Soft Skills
- Communication
- Problem Solving

# Strengths

- Point 1
- Point 2
- Point 3

# Weaknesses

- Point 1
- Point 2
- Point 3

# Missing Skills

List all important skills missing for the target role.
Include technical tools, frameworks, certifications, and soft skills.

# Improvement Suggestions

- Point 1
- Point 2
- Point 3

# Recommended Career Roles

Recommend 5–10 realistic roles based on skills, education, projects, and experience.

# Recommended Projects

Project 1:
- Project Name:
- Skills Used:
- Difficulty:
- What the candidate will learn:

Project 2:
- Project Name:
- Skills Used:
- Difficulty:
- What the candidate will learn:

Project 3:
- Project Name:
- Skills Used:
- Difficulty:
- What the candidate will learn:

# Interview Questions

Generate:

## Easy Questions
- 5 questions

## Medium Questions
- 5 questions

## Advanced Questions
- 5 questions

Provide answers for each question.

# Learning Roadmap

Week 1:

Topics to Learn:
- ...

Free Resources:
- ...

Mini Project:
- ...

Expected Outcome:
- ...

Week 2:

Topics to Learn:
- ...

Free Resources:
- ...

Mini Project:
- ...

Expected Outcome:
- ...

Week 3:

Topics to Learn:
- ...

Free Resources:
- ...

Mini Project:
- ...

Expected Outcome:
- ...

Week 4:

Topics to Learn:
- ...

Free Resources:
- ...

Mini Project:
- ...

Expected Outcome:
- ...
# Job Match Analysis

Match Score: X/100

Matching Skills:

List every matching skill found between the resume and job description.
# Missing ATS Keywords

List important keywords present in the Job Description but missing from the resume.

Example:
- Tableau
- AWS
- Git
- PostgreSQL
- Azure

# High Priority Keywords

List the most important keywords that should appear multiple times in the resume.

Example:
- Python
- SQL
- Power BI
- Data Analysis
- Machine Learning

# Missing Skills

- Skill 1
- Skill 2
- Skill 3

# Top Resume Improvements

- Improvement 1
- Improvement 2
- Improvement 3

# Final Recruiter Verdict

Provide a professional recruiter summary in 3-5 bullet points covering:
- Employability level
- Job readiness
- Key improvements needed
- Best next step

Job Description:
{job_description if job_description else "No job description provided."}

Resume:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
def rewrite_resume(resume_text):
    prompt = f"""
Rewrite this resume in professional ATS-friendly format.

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
def generate_interview_questions(resume_text):

    prompt = f"""
You are a Senior Technical Interviewer.

Generate:
- 5 Easy Questions with Answers
- 5 Medium Questions with Answers
- 5 Advanced Questions with Answers
- 5 HR Questions with Answers

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def generate_cover_letter(resume_text, job_description):

    prompt = f"""
Create a professional cover letter.

Job Description:
{job_description}

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def generate_linkedin_profile(resume_text):

    prompt = f"""
You are a LinkedIn branding expert.

Create a complete LinkedIn profile based on this resume.

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
def generate_job_suggestions(resume_text):
    prompt = f"""
You are a career advisor.

Based on this resume, suggest:
- 10 suitable job roles
- Why each role fits
- Entry level or experienced level
- Skills needed for each role

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def generate_skill_gap(resume_text, job_description):
    prompt = f"""
You are a career expert and ATS analyzer.

Compare the resume with the job description and give:

1. Current Skills
2. Missing Skills
3. Skill Gap Analysis
4. Priority Skills to learn first
5. Learning Roadmap (short)
6. Job readiness score (out of 100)

Be very clear and structured.

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# Streamlit UI
st.set_page_config(
        page_title="Zyphora AI",
        page_icon="🚀",
        layout="wide"
)
st.markdown("""
<style>
.stButton > button {
    border-radius: 12px;
    height: 50px;
    font-weight: bold;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)


with  st.sidebar:
      st.title("🚀 Zyphora AI")
      st.caption(
    "AI-powered ATS Resume Analysis, Career Guidance & Learning Roadmap"
)

      st.info("""
Upload your resume and get:
✅ ATS Score
✅ Job Match Score
✅ Skills Analysis
✅ Career Recommendations
✅ Learning Roadmap
✅ Recruiter Feedback
""")
      st.subheader("💰 Pricing Plans")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
🆓 Free Plan

• ATS Score
• Basic Resume Analysis
• 3 Uses Daily
""")

    if user_plan == "free":
        st.success("✅ Current Plan")

with col2:
    st.success("""
💎 Pro Plan - ₹99

• Full ATS Report
• Resume Rewrite
• Skill Gap Analysis
""")

    if user_plan == "pro":
        st.success("✅ Current Plan")
    else:
        if st.button("💎 Upgrade to Pro"):
            st.info("🚧 Razorpay payment will be added here.")

with col3:
    st.warning("""
🚀 Premium Plan - ₹199

• Cover Letter
• Interview Questions
• LinkedIn Profile
• Everything Included
""")

    if user_plan == "premium":
        st.success("✅ Current Plan")
    else:
        if st.button("🚀 Upgrade to Premium"):
            st.info("🚧 Razorpay payment will be added here.")
            
    # 🔴 ADD THIS BELOW INFO BOX
# if st.button("🚪 Logout"):
#         st.session_state["logged_in"] = False
#         st.rerun()
    st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: bold;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Zyphora AI")
st.markdown("""
### Smart Resume Analyzer

Get:

✅ ATS Score
✅ Job Match Score
✅ Skills Analysis
✅ Career Recommendations
✅ Learning Roadmap
✅ Recruiter Feedback
""")
if page == "Resume Analyzer":

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"]
    )

    job_description = st.text_area(
        "Paste Job Description (Optional)"
    )

    if uploaded_file is not None:

        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("File size must be under 5 MB")
            st.stop()

        with st.spinner("AI is thinking... 🤖"):
            resume_text = extract_text_from_pdf(uploaded_file)
            word_count = len(resume_text.split())

        st.info(f"📄 Resume Word Count: {word_count}")
        st.success("Resume Uploaded Successfully!")

    # =========================
    # BUTTONS SECTION
    # =========================

    col1, col2, col3= st.columns(3)
    
    with col1:
     analyze_btn = st.button("📊 Analyze Resume")
     rewrite_btn = st.button("📝 Rewrite Resume")

    with col2:
     interview_btn = st.button("🎤 Interview Questions")
     cover_btn = st.button("📄 Cover Letter")
    with col3:
 
     linkedin_btn = st.button("🔗 LinkedIn Profile")
     skill_gap_btn = st.button("📊 Skill Gap Analysis")
     job_btn = st.button("💼 Job Suggestions")

    # =========================
    # ANALYZE LOGIC
    # =========================

    if analyze_btn:
     if users[username]["plan"] == "free":
      users[username]["usage_count"] += 1
      save_users(users)

     with st.spinner("Analyzing Resume..."):
        result = analyze_resume(resume_text, job_description)

        st.markdown(result)

        st.download_button(
            "📥 Download Report",
            data=result,
            file_name="ATS_Report.txt",
            mime="text/plain"
    )

# =========================
# REWRITE LOGIC
# ========================
    if rewrite_btn:
     try:

        if user_plan not in ["pro", "premium"]:
            st.warning("🔒 Resume Rewrite is available in Pro Plan (₹99) and Premium Plan (₹199)")

        else:
            with st.spinner("Rewriting Resume..."):

                rewritten_resume = rewrite_resume(resume_text)

                st.markdown(rewritten_resume)

                st.download_button(
                    "📥 Download Improved Resume",
                    data=rewritten_resume,
                    file_name="Zyphora_Resume_Rewrite.txt",
                    mime="text/plain"
                )

     except Exception as e:
        st.error(f"Error: {e}")

# =========================
# INTERVIEW QUESTIONS
# =========================
    if interview_btn:
     try:

        if user_plan != "premium":
            st.warning("🔒 Interview Questions are available in Premium Plan (₹199)")
        else:
            interview_result = generate_interview_questions(resume_text)

            st.markdown(interview_result)

            st.download_button(
                "📥 Download Interview Questions",
                data=interview_result,
                file_name="Zyphora_Interview_Questions.txt",
                mime="text/plain"
            )

     except Exception as e:
        st.error(f"Error: {e}")

# =========================
# COVER LETTER
# =========================
    if cover_btn:
     try:

        if user_plan != "premium":
            st.warning("🔒 Cover Letter is available in Premium Plan (₹199)")

        else:
            with st.spinner("Generating Cover Letter..."):

                cover_letter = generate_cover_letter(
                    resume_text,
                    job_description
                )

                st.markdown(cover_letter)

                st.download_button(
                    "📥 Download Cover Letter",
                    data=cover_letter,
                    file_name="Zyphora_Cover_Letter.txt",
                    mime="text/plain"
                )

     except Exception as e:
        st.error(f"Error: {e}")

# =========================
# LINKEDIN PROFILE
# =========================
    if linkedin_btn:
     try:

        if user_plan != "premium":
            st.warning("🔒 LinkedIn Profile is available in Premium Plan (₹199)")

        else:
            with st.spinner("Creating LinkedIn Profile..."):

                linkedin_profile = generate_linkedin_profile(
                    resume_text
                )

                st.markdown(linkedin_profile)

                st.download_button(
                    "📥 Download LinkedIn Profile",
                    data=linkedin_profile,
                    file_name="Zyphora_LinkedIn_Profile.txt",
                    mime="text/plain"
                )

     except Exception as e:
        st.error(f"Error: {e}")
# =========================
# skill_gap
# =========================
      
    if skill_gap_btn:
     try:

        if user_plan not in ["pro", "premium"]:
            st.warning("🔒 Skill Gap Analysis is available in Pro Plan (₹99) and Premium Plan (₹199)")

        else:
            with st.spinner("Analyzing skill gaps..."):

                result = generate_skill_gap(
                    resume_text,
                    job_description
                )

                st.markdown(result)

                st.download_button(
                    "📥 Download Skill Gap Report",
                    data=result,
                    file_name="Zyphora_Skill_Gap_Report.txt",
                    mime="text/plain"
                )

     except Exception as e:
        st.error(f"Error: {e}")
        
# =========================
# job_btn
# ========================= 
    
    if job_btn:
     try:

        if user_plan not in ["pro", "premium"]:
            st.warning("🔒 Job Suggestions are available in Pro Plan (₹99) and Premium Plan (₹199)")

        else:
            with st.spinner("Finding suitable jobs..."):

                result = generate_job_suggestions(
                    resume_text
                )

                st.markdown(result)

                st.download_button(
                    "📥 Download Job Suggestions",
                    data=result,
                    file_name="Zyphora_Job_Suggestions.txt",
                    mime="text/plain"
                )

     except Exception as e:
        st.error(f"Error: {e}")
if page == "Pricing":

    st.title("💎 ZyphoraAI Plans")

    st.subheader("🆓 Free")
    st.write("3 analyses per day")

    st.subheader("💎 Pro - ₹99/month")
    st.write("Unlimited analyses")

    st.subheader("🚀 Premium - ₹199/month")
    st.write("Unlimited analyses + future premium tools")

if st.button("💎 Upgrade to Pro"):
    users[username]["plan"] = "pro"
    save_users(users)
    st.success("Upgraded to Pro!")
    st.rerun()

if st.button("🚀 Upgrade to Premium"):
    users[username]["plan"] = "premium"
    save_users(users)
    st.success("Upgraded to Premium!")
    st.rerun()