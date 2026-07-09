import streamlit as st

st.set_page_config(page_title="Payment", page_icon="💳")

st.title("💳 Upgrade Your Plan")

# Get selected plan
plan = st.session_state.get("selected_plan", "free")

if plan == "pro":
    price = "₹99/month"
    features = [
        "✅ Unlimited Resume Analysis",
        "✅ Resume Rewrite",
        "✅ Skill Gap Analysis",
        "✅ Advanced ATS Report"
    ]
elif plan == "premium":
    price = "₹199/month"
    features = [
        "✅ Everything in Pro",
        "✅ Cover Letter Generator",
        "✅ Interview Questions",
        "✅ LinkedIn Profile Optimizer",
        "✅ Future Premium Features"
    ]
else:
    price = "Free"
    features = ["Basic Features"]

st.subheader(f"Selected Plan: {plan.upper()}")
st.subheader(f"Price: {price}")

st.markdown("### You'll get:")

for feature in features:
    st.write(feature)

st.divider()

st.warning("🚧 Razorpay account is under review.")

st.info(
    "Once your Razorpay account is activated, this page will open the secure payment gateway automatically."
)

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅ Back"):
        st.switch_page("app.py")

with col2:
    if st.button("💳 Proceed to Payment"):
        st.success("Payment gateway will be connected after Razorpay approval.")