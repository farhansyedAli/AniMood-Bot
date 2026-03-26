import gradio as gr
import os
import requests
import random

# Load API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"

# Bot system message
SYSTEM_PROMPT = """
You are AniMoodBot, a friendly and helpful anime expert. You recommend anime based on the user's mood, genre preference, and desired episode length.
You're fun and informative like a fellow anime fan. Keep responses clear and engaging.
Include a brief reason why each anime matches the mood/genre combo. If possible, mention the number of episodes.
"""

# Mood and genre options
MOOD_OPTIONS = ["Happy", "Sad", "Adventurous", "Chill", "Bored", "Excited", "Romantic"]
GENRE_OPTIONS = ["Action", "Romance", "Slice of Life", "Fantasy", "Mystery", "Comedy", "Psychological", "Sci-Fi", "Sports"]

def build_prompt(mood, genre, length):
    prompt = f"My mood is '{mood}', I like the '{genre}' genre, and I'd prefer something with "
    if length <= 12:
        prompt += "a very short number of episodes (under 12)."
    elif length <= 25:
        prompt += "a short series (under 25 episodes)."
    elif length <= 50:
        prompt += "a medium-length series (around 50 episodes)."
    else:
        prompt += "a long series (over 50 episodes)."
    prompt += " Please recommend an anime that matches this."
    return prompt

def query_groq(user_message, chat_history):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": user_message})

    response = requests.post(GROQ_API_URL, headers=headers, json={
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7
    })

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    else:
        return f"Error {response.status_code}: {response.text}"

def respond(mood, genre, length, chat_history):
    prompt = build_prompt(mood, genre, length)
    bot_reply = query_groq(prompt, chat_history)
    chat_history.append((prompt, bot_reply))
    return chat_history

def surprise(chat_history):
    mood = random.choice(MOOD_OPTIONS)
    genre = random.choice(GENRE_OPTIONS)
    length = random.choice([12, 25, 50, 100])
    prompt = build_prompt(mood, genre, length)
    bot_reply = query_groq(prompt, chat_history)
    chat_history.append((f"🎲 Surprise me! ({mood}, {genre}, ~{length} episodes)", bot_reply))
    return chat_history

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 AniMoodBot - Your Anime Recommendation Buddy")
    gr.Markdown("Tell me your mood, favorite genre, and how many episodes you'd prefer. Or hit **Surprise Me!** to get a random pick.")

    chatbot = gr.Chatbot()
    state = gr.State([])

    with gr.Row():
        mood_dropdown = gr.Dropdown(label="How are you feeling?", choices=MOOD_OPTIONS, value="Happy")
        genre_dropdown = gr.Dropdown(label="Favorite genre?", choices=GENRE_OPTIONS, value="Action")
        episode_slider = gr.Slider(label="Max episodes?", minimum=1, maximum=100, value=25, step=1)

    with gr.Row():
        submit = gr.Button("🎌 Get Recommendation")
        surprise_btn = gr.Button("🎲 Surprise Me!")
        clear_btn = gr.Button("🧹 Clear Chat")

    submit.click(fn=respond, inputs=[mood_dropdown, genre_dropdown, episode_slider, state], outputs=[chatbot])
    surprise_btn.click(fn=surprise, inputs=[state], outputs=[chatbot])
    clear_btn.click(lambda: ([], []), None, [chatbot, state])

demo.launch()
