import streamlit as st
import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

users = load_users()

if "username" not in st.session_state:
    st.warning("Please login first.")
    st.switch_page("app.py")

username = st.session_state["username"]

user = users[username]

st.set_page_config(page_title="My Account", page_icon="👤")

st.title("👤 My Account")

st.write(f"### Username: {username}")
st.write(f"### Plan: {user['plan'].upper()}")
st.write(f"### Today's Usage: {user['usage_count']}")

st.divider()

if user["plan"] == "free":

    st.warning("You are using the Free Plan.")

    if st.button("💎 Upgrade to Pro"):
        st.session_state["selected_plan"] = "pro"
        st.switch_page("pages/payment.py")

    if st.button("🚀 Upgrade to Premium"):
        st.session_state["selected_plan"] = "premium"
        st.switch_page("pages/payment.py")

elif user["plan"] == "pro":

    st.success("You are a Pro User.")

    if st.button("🚀 Upgrade to Premium"):
        st.session_state["selected_plan"] = "premium"
        st.switch_page("pages/payment.py")

else:
    st.success("🚀 Premium User")

st.divider()

if st.button("🚪 Logout"):
    st.session_state.clear()
<<<<<<< HEAD
    st.switch_page("app.py")
=======
    st.switch_page("app.py")
>>>>>>> 86cb616afda488f3c3ed315a179361b645671f01
