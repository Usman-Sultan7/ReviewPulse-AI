import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1. Page Configuration
st.set_page_config(
    page_title="ReviewPulse AI", 
    page_icon="🛍️", 
    layout="centered"
)

# 2. Initialize Session State Variables
if "api_authenticated" not in st.session_state:
    st.session_state["api_authenticated"] = False
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 3. Lock Screen: Ask for API Key First
if not st.session_state["api_authenticated"]:
    st.title("🔐 ReviewPulse AI - Access Portal")
    st.write("Please enter your OpenAI API Key to unlock the sentiment analysis dashboard.")

    # API Key Input Form
    api_key_input = st.text_input("OpenAI API Key", type="password")

    if st.button("Unlock Dashboard"):
        if api_key_input.strip() != "":
            st.session_state["api_key"] = api_key_input.strip()
            st.session_state["api_authenticated"] = True
            st.rerun()  # Refresh app to load the main interface
        else:
            st.error("Please enter a valid API key to proceed.")

    # Stop execution here so the dashboard doesn't load until unlocked
    st.stop()

# ==========================================
# 4. MAIN INTERFACE (Loaded after unlock)
# ==========================================
st.title("🛍️ ReviewPulse AI")
st.caption("Transform messy customer reviews into actionable insights, satisfaction scores, and feedback trends instantly.")

# Define the expert system prompt role for the e-commerce analyst
system_prompt = (
    "You are an expert e-commerce data analyst and sentiment specialist. "
    "When a user provides product reviews or customer feedback, analyze them thoroughly and output a structured report containing: "
    "1. Overall Satisfaction Score (out of 10). "
    "2. Top 3 positive aspects (Pros) praised by customers. "
    "3. Top 3 negative aspects (Cons) or complaints reported. "
    "4. A brief actionable recommendation for the seller. "
    "Keep the layout clean using markdown headers and bullet points."
)

# Ensure System Message is tracked in session history
if not any(isinstance(x, SystemMessage) for x in st.session_state["messages"]):
    st.session_state["messages"].append(SystemMessage(content=system_prompt))

# Display prior chat messages/reports
for msg in st.session_state["messages"][1:]:  # Skip showing the raw system message
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 5. Bottom Center Chat Input (Automatically pinned by Streamlit)
if user_prompt := st.chat_input("Paste your product reviews or feedback here..."):
    
    # Append user input to history and display it
    st.session_state["messages"].append(HumanMessage(content=user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Initialize Chat model with the user-provided API key
    try:
        chat_model = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=st.session_state["api_key"]
        )

        # Generate AI Sentiment Analysis Response inside a spinner
        with st.chat_message("assistant"):
            with st.spinner("Analyzing customer review patterns..."):
                response = chat_model.invoke(st.session_state["messages"])
                st.markdown(response.content)

                # Save AI response to message history
                st.session_state["messages"].append(AIMessage(content=response.content))

    except Exception as e:
        st.error(f"An error occurred while communicating with the OpenAI API: {e}")