
import os
import sys
import time
import json
import subprocess
import re
import datetime
import speech_recognition as sr
import streamlit as st
from services.voice_engine import record_and_transcribe
from services.voice_player import speak

from openai import OpenAI
from dotenv import load_dotenv
from importlib import import_module

# Project root (for `components/`) and `app/` (for `services/`) on sys.path
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_APP_DIR, ".."))
for _p in (_ROOT_DIR, _APP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Streamlit page configuration
st.set_page_config(
    page_title="🧠 Convo AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile CSS styling for responsiveness
st.markdown("""
<style>
@media screen and (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    .stButton button { font-size: 0.9rem !important; padding: 0.5rem 1rem !important; }
    .stMarkdown h1, .stMarkdown h2 { font-size: 1.2rem !important; }
    .stSelectbox, .stTextInput { font-size: 0.9rem !important; }
}
</style>
""", unsafe_allow_html=True)

# Load learning progression from JSON if it exists
learning_map = {}
json_path = "data/learning_progression.json"

if os.path.exists(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                learning_map = json.loads(content)
            else:
                st.sidebar.warning("⚠️ learning_progression.json is empty.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Failed to load learning_progression.json: {e}")
else:
    st.sidebar.warning("⚠️ Please upload a learning_progression.json file in the sidebar.")

# File uploader in case JSON doesn't exist
uploaded_file = st.sidebar.file_uploader("📁 Upload Learning Progression JSON", type="json")
if uploaded_file is not None:
    file_path = os.path.join("data", "learning_progression.json")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Uploaded successfully! Please reload to apply.")

# Import internal services and UI components
from services.persona_engine import build_persona_prompt
from services.feedback_engine import build_feedback_prompt
from services.scoring_engine import build_score_prompt
from services.scenario_engine import get_scenario, list_scenario_names
from services.gamification_engine import calculate_xp, check_streak
from services.voice_engine import record_and_transcribe
from services.interruption_engine import get_interruption_behavior
from services.personality_evolution import evaluate_user_tone
from services.multi_agent_engine import get_panel, MULTI_PANEL
from services.emotion_engine import evaluate_emotional_tone
from services.memory_engine import update_memory, get_memory_context
from services.skill_tracker import (
    get_lowest_trait, init_skill_tracker, get_skill_averages,
    update_skills, get_skill_timeseries
)
from services.voice_personality_engine import choose_voice_profile
from services.animation_registry import get_animation_for_subdomain
from services.ui.subdomain_visuals import get_subdomain_visual
from services.voice_player import speak
from components.ui_blocks import (
    show_skill_dashboard, show_emotion_radar, show_score,
    show_feedback, show_conversation_history, show_progress_chart
)
from components.skill_map import show_skill_map
from components.domain_styles import get_domain_style

# Initialize session state with defaults
def init_state():
    defaults = {
        "xp": 0, "streak": 0, "last_used": None, "memory": [],
        "skills": init_skill_tracker(), "daily_goal": 3, "daily_progress": 0,
        "daily_completed": False, "favorability_streak": 0,
        "last_spoken_text": "", "favorability_scores": [],
        "conversation_turns": [], "ai_responses": [], "feedback_history": [],
        "conversation_timer": {
            "start_time": None, "end_time": None,
            "time_limit_seconds": None, "expired": False
        }
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# Initialize environment
init_state()
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure session_state keys for conversation defaults
for _key in ("scenario_context", "goal", "persona", "selected_traits"):
    if _key not in st.session_state:
        st.session_state[_key] = ""


# Sidebar for Skill Map, Domain and Timer
with st.sidebar:
    st.markdown("## 🗺️ Skill Map")
    show_skill_map()

    st.markdown("## 🎓 Domain")
    DOMAIN_MODULES = {
        "Political Science": "services.domains.political_conversation",
        "Business Communication": "services.domains.business_communication",
        "Philosophy": "services.domains.philosophy",
        "Emotional Intelligence": "services.domains.emotional_intelligence",
        "Debate Simulation": "services.domains.debate_simulation",
        "Satirical Political Commentary": "services.domains.satirical_political_commentary",
        "Artificial Intelligence & Society": "services.domains.ai_society",
        "Sales Talk": "services.domains.sales_conversation"
    }
    selected_domain = st.selectbox("Choose Domain", list(DOMAIN_MODULES.keys()))
    domain_module = import_module(DOMAIN_MODULES[selected_domain])
    subdomains = domain_module.get_subdomains()
    selected_subdomain = st.selectbox("Subdomain", subdomains)

    st.markdown("## ⏲️ Timer")
    time_limit_options = {
        "1 min": 60, "3 min": 180, "5 min": 300, "10 min": 600, "Unlimited": None
    }
    selected_limit = st.selectbox("Set Limit", list(time_limit_options.keys()))
    st.session_state.conversation_timer["time_limit_seconds"] = time_limit_options[selected_limit]

    if st.button("▶️ Start Timer"):
        st.session_state.conversation_timer["start_time"] = time.time()
        if st.session_state.conversation_timer["time_limit_seconds"]:
            st.session_state.conversation_timer["end_time"] = (
                st.session_state.conversation_timer["start_time"] +
                st.session_state.conversation_timer["time_limit_seconds"]
            )

    start = st.session_state.conversation_timer["start_time"]
    end = st.session_state.conversation_timer["end_time"]
    if start and end:
        now = time.time()
        remaining = int(end - now)
        if remaining > 0:
            st.markdown(f"⏳ Time left: **{remaining//60}:{remaining%60:02d}**")
        else:
            st.session_state.conversation_timer["expired"] = True
            st.error("⏰ Time's up!")
            st.stop()
    elif start and not end:
        st.success("✅ Unlimited mode")

# Visual domain tone and UI
style_data = get_domain_style(selected_domain, selected_subdomain)
st.markdown(f"<style>body {{ background: {style_data['background']}; }}</style>", unsafe_allow_html=True)
st.markdown(f"## {style_data['emoji']} Tone: {style_data['tone'].capitalize()}")

animation = get_animation_for_subdomain(selected_subdomain)
visual_config = get_subdomain_visual(selected_subdomain)
st.markdown(f"""
<div class="{visual_config['animation']}" style="
    padding: 1rem; border-radius: 10px;
    background: {visual_config['bg_gradient']};
    color: white; font-size: 1.2rem;
    margin-bottom: 1rem;">
<b>{visual_config['persona_label']}</b> Now simulating: <u>{selected_subdomain}</u>
</div>
""", unsafe_allow_html=True)

# Conversation input area (Speech-to-Text + Text)
st.markdown("### 🎤 Voice Input")
uploaded_audio = st.file_uploader("Upload an audio file (wav/mp3/ogg)", type=["wav", "mp3", "ogg"])
if uploaded_audio:
    try:
        user_input = record_and_transcribe(uploaded_audio)
        st.markdown("**Transcribed Text:**")
        st.write(user_input)
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        user_input = ""
else:
    user_input = st.text_input("You:", placeholder="Type your response here...")

# Multi-agent panel support
use_panel = st.checkbox("👥 Simulate Multi-Agent Panel?", value=False)
panel_data = []
if use_panel:
    panel_name = st.selectbox("Choose Panel", list(MULTI_PANEL.keys()))
    panel_data = get_panel(panel_name)
    if panel_data:
        st.info(f"👥 Panel Selected: {panel_name}")

if user_input:
    memory_context = ""
    for i in range(max(0, len(st.session_state.conversation_turns) - 3), len(st.session_state.conversation_turns)):
        memory_context += f"User: {st.session_state.conversation_turns[i]}\n"
        memory_context += f"AI: {st.session_state.ai_responses[i]}\n"

    interrupt_note = get_interruption_behavior(len(user_input.split()))
    tone_observation = evaluate_user_tone(user_input)

    combined_context = memory_context
    if st.session_state.scenario_context:
        combined_context += f"\n\nScenario context: {st.session_state.scenario_context}"
    if interrupt_note:
        combined_context += f"\n\nAI Behavior Rule: {interrupt_note}"
        st.caption(f"🗯️ AI may interrupt: {interrupt_note}")
    if tone_observation:
        combined_context += f"\n\nRecent User Tone: {tone_observation}"
        st.caption(f"🧠 AI will adapt: {tone_observation}")

    memory_context = get_memory_context(st.session_state.memory)

    domain_prompt = domain_module.generate_prompt(
        user_input=user_input,
        subdomain=selected_subdomain,
        goal=st.session_state.goal,
        memory=combined_context,
        traits=st.session_state.selected_traits
    )

    system_prompt = domain_prompt["prompt"] if isinstance(domain_prompt, dict) else domain_prompt

    agent_responses = []

    try:
        if panel_data:
            for agent in panel_data:
                agent_prompt = f"""
You are {agent['name']} speaking in a panel simulation.
Your tone is {agent['tone']}.
Your role: {agent['role']}
The user is trying to: {st.session_state.goal}
Context: {combined_context}
Respond naturally to:
\"{user_input}\"
"""
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": agent_prompt}]
                )
                ai_msg = response.choices[0].message.content
                agent_responses.append((agent["name"], ai_msg))
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            ai_msg = response.choices[0].message.content
            agent_responses.append(("AI", ai_msg))
        st.session_state.last_spoken_text = ai_msg
        # Auto-play AI response as voice
        try:
            speak(ai_msg)
        except Exception as e:
            st.warning(f"TTS error: {e}")

        # Display the AI responses
        full_response = ""
        st.markdown("🧑‍💼 AI Panel Responses:")
        for name, msg in agent_responses:
            st.markdown(f"### {animation['emoji']} {selected_subdomain}")
            st.markdown(f"""<div class="{animation['css_class']}">
                <p style="font-size: 1.1rem; line-height: 1.6;">{msg}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            full_response += f"{name}: {msg}\n"

        st.session_state.ai_responses.append(full_response)

        # Emotional Tone Evaluation
        emotion_prompt = evaluate_emotional_tone(user_input, st.session_state.goal)
        emotion_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a communication analyst."},
                {"role": "user", "content": emotion_prompt}
            ]
        )
        raw_emotion_output = emotion_response.choices[0].message.content.strip()
        try:
            emotion_data = json.loads(raw_emotion_output)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', raw_emotion_output, re.DOTALL)
            if json_match:
                emotion_data = json.loads(json_match.group())
            else:
                st.warning("⚠️ Could not parse emotional analysis.")
                st.text(f"Raw output:\n{raw_emotion_output}")
                emotion_data = {
                    "clarity": 5, "confidence": 5, "empathy": 5,
                    "positivity": 5, "assertiveness": 5,
                    "insight": "No insight available."
                }

        show_emotion_radar(emotion_data)
        skill_scores = {
            "clarity": emotion_data.get("clarity", 0),
            "confidence": emotion_data.get("confidence", 0),
            "empathy": emotion_data.get("empathy", 0),
            "positivity": emotion_data.get("positivity", 0),
            "persuasiveness": emotion_data.get("assertiveness", 0)
        }

        # Coaching Tip
        lowest_trait = get_lowest_trait(emotion_data)
        if lowest_trait:
            coaching_prompt = f"""You are a communication coach. The user is trying to improve their '{lowest_trait}'.

Their last message was:
\"{user_input}\"

Give 1 powerful but concise sentence to help them improve their {lowest_trait}.
"""
            coaching_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Only return one clear sentence of advice."},
                    {"role": "user", "content": coaching_prompt}
                ]
            )
            coaching_tip = coaching_response.choices[0].message.content.strip()
            st.markdown(f"### 🎯 Targeted Coaching: *{lowest_trait.capitalize()}*")
            st.info(coaching_tip)

        # Update skills and show insight
        st.session_state.skills = update_skills(st.session_state.skills, skill_scores)
        st.info(f"💡 Tip: {emotion_data.get('insight', 'No insight available.')}")

        # Scoring
        score_prompt = build_score_prompt(st.session_state.goal, user_input, scoring_mode="basic")
        score_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Respond only with a number between 0 and 100."},
                {"role": "user", "content": score_prompt}
            ]
        )
        try:
            score = int(score_response.choices[0].message.content.strip())
            score = max(0, min(100, score))
        except:
            score = 50

        show_score(score)
        st.session_state.favorability_scores.append(score)
        st.session_state.conversation_turns.append(user_input)

        # Daily goal tracking
        if not st.session_state.daily_completed:
            st.session_state.daily_progress += 1
            if st.session_state.daily_progress >= st.session_state.daily_goal:
                st.session_state.daily_completed = True
                st.balloons()
                st.success("🎉 Daily Goal Complete! You're building momentum.")

        gained_xp = calculate_xp(score)
        st.session_state.xp += gained_xp
        st.success(f"🏆 +{gained_xp} XP earned!")

        today = datetime.date.today()
        if st.session_state.last_used != today:
            streak_result, valid = check_streak(st.session_state.last_used)
            st.session_state.streak = st.session_state.streak + streak_result if valid else 1
            st.session_state.last_used = today

        if score >= 80:
            st.session_state.favorability_streak += 1
        else:
            st.session_state.favorability_streak = 0

        if st.session_state.favorability_streak >= 3:
            st.success("🎯 Goal Achieved! You're consistently hitting the right notes!")

        # Reflection
        if st.session_state.daily_completed and "reflection_shown" not in st.session_state:
            st.session_state.reflection_shown = True
            skill_averages = get_skill_averages(st.session_state.skills)
            from services.reflection_engine import generate_reflection
            reflection_prompt = generate_reflection(
                tone_observation if tone_observation else "neutral",
                lowest_trait,
                skill_averages,
                st.session_state.streak,
                st.session_state.daily_progress
            )
            reflection_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a motivating reflection coach."},
                    {"role": "user", "content": reflection_prompt}
                ]
            )
            reflection = reflection_response.choices[0].message.content.strip()
            st.markdown("## 🌟 Daily Reflection")
            st.info(reflection)

        # Feedback
        feedback_prompt = build_feedback_prompt(st.session_state.goal, st.session_state.conversation_turns, style="coach")
        feedback_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Respond with one sentence only."},
                {"role": "user", "content": feedback_prompt}
            ]
        )
        feedback_text = feedback_response.choices[0].message.content.strip()
        st.session_state.feedback_history.append(feedback_text)
        show_feedback(feedback_text)

        # Memory Update
        st.session_state.memory = update_memory(
            st.session_state.memory,
            user_input,
            agent_responses[-1][1] if use_panel and agent_responses else ai_msg,
            tone_observation if tone_observation else "",
            score,
            feedback_text
        )

# History and Charts
    except Exception as e:
        st.error(f"⚠️ API Error: {e}")
show_conversation_history(
    st.session_state.conversation_turns,
    st.session_state.ai_responses,
    st.session_state.favorability_scores,
    st.session_state.feedback_history
)

# Progress Chart (custom)
try:
    import matplotlib.pyplot as plt
    scores = st.session_state.favorability_scores
    if scores:
        fig, ax = plt.subplots()
        ax.plot(range(1, len(scores)+1), scores, marker='o')
        ax.set_xlabel('Turn')
        ax.set_ylabel('Favorability Score')
        st.pyplot(fig)
except Exception as e:
    st.warning(f"Could not render progress chart: {e}")
st.markdown(f"🌟 XP: {st.session_state.xp} | 🔥 Streak: {st.session_state.streak} days")

# Skill Intelligence Summary
st.markdown("## 🧠 Skill Intelligence Summary")
timeseries = get_skill_timeseries(st.session_state.skills)
show_skill_dashboard(timeseries)

# Export Conversation
if st.button("📤 Export Conversation"):
    export_text = "Convo AI Session Transcript\n\n"
    for i in range(len(st.session_state.conversation_turns)):
        export_text += f"User: {st.session_state.conversation_turns[i]}\n"
        export_text += f"AI: {st.session_state.ai_responses[i]}\n"
        if i < len(st.session_state.favorability_scores):
            export_text += f"Favorability: {st.session_state.favorability_scores[i]}/100\n"
        if i < len(st.session_state.feedback_history):
            export_text += f"Feedback: {st.session_state.feedback_history[i]}\n"
        export_text += "------\n"

    with open("convo_ai_export.txt", "w", encoding="utf-8") as f:
        f.write(export_text)
    with open("convo_ai_export.txt", "rb") as file:
        st.download_button("⬇️ Download Transcript", file, file_name="convo_ai_export.txt")

# Voice Replay (Manual)
st.markdown("### 🔁 Voice Controls")
col1, col2 = st.columns(2)
if "last_spoken_text" in st.session_state:
    with col1:
        if st.button("🔄 Replay Last AI Voice"):
            from services.voice_player import speak
            speak(st.session_state.last_spoken_text)

# Reset Button
if st.button("🔄 Reset Conversation"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
