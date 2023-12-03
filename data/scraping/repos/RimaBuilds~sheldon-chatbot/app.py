import openai
import os 
import re
import random
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# Set up OpenAI API key and engine
openai.api_key = os.environ.get("OPENAI_API_KEY")
engine = "text-davinci-003"

# Load Sheldon Cooper quotes from text file
with open("sheldon.txt", "r") as file:
    sheldon_quotes = file.readlines()
    sheldon_quotes = [quote.strip() for quote in sheldon_quotes]

# Keep track of the last response generated by the bot
last_response = ""

# Function to generate response from GPT-3 model
conversation_history = []

def generate_response(user_input):
    global conversation_history, last_response

    conversation_history.append(f"User: {user_input}")
    
    if len(conversation_history) > 4:  # Keep conversation history to the last 4 messages
        conversation_history.pop(0)
    
    try:
        if user_input.lower() == last_response.lower():
            return "I'm sorry, I don't have anything new to add."
        
        prompt = ("You are chatting with a chatbot that speaks like Sheldon Cooper from The Big Bang Theory. "
          "The chatbot should respond as Sheldon would in a conversation in a very funny way and using "
          "some of his catchphrases. The conversation so far is as follows:\n\n")
        prompt += "\n".join(conversation_history)
        prompt += "\nSheldon, please respond in a funny way.\n"
        prompt += "\nSheldon:"

        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=1.2,
            presence_penalty=0.5,
            frequency_penalty=0.5,
        )

        message = response.choices[0].text.strip()

        # Remove quotes from the message
        message = message.replace('"', '')

        # Check if the response is the same as the user input
        if message.lower() == user_input.lower():
            return "I'm sorry, I don't have anything new to add."

        # Update the last_response variable and add it to the conversation history
        last_response = message
        conversation_history.append(f"Sheldon: {message}")

        return message
    except Exception as e:
        print("Error generating response:", e)


# Create Flask app
app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('home.html')

# Chatbot page route
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['text']
        response = generate_response(user_input)
        return render_template('chatbot.html', response_text=response)
    else:
        return render_template('chatbot.html', response_text="")
    
# Route to get response from chatbot
@app.route('/get-response', methods=['POST'])
def get_response():
    user_input = request.form['text']
    prompt = f"Sheldon Cooper says: {user_input}\nSheldon Cooper also says:"
    response = generate_response(prompt)
    response = response.replace("Sheldon Cooper also says:", "")
    return response.strip()

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)