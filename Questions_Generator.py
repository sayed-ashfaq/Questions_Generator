from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import sqlite3 # trying this out - find Langchain memory
import streamlit as st


# load environment variable from .env file
load_dotenv()
genai_key= os.environ.get("GOOGLE_API_KEY")

model= ChatGoogleGenerativeAI(
    model= 'gemini-2.0-flash',
    temperature= 0.6
)

prompt_template= PromptTemplate(
    input_variables= ['topic', 'level', 'n_questions'],
    template= "I am currently learning the topic {topic}, But I want to test myself, so give me {n_questions} questions to evaluate myself based on difficulty level {level}. Give all questions randomly for the use case like for Interview, Used often professionally etc"
)

# set up SQLite database
def init_db():
    conn= sqlite3.connect("users.db")
    c= conn.cursor()
    c.execute('''Create TABLE IF NOT EXISTS users
                    (name TEXT, topic TEXT, level TEXT)''')
    conn.commit()
    conn.close()

def save_user_preferences(name, topic, level):
    conn= sqlite3.connect("users.db")
    c= conn.cursor()
    c.execute("INSERT INTO users (name, topic, level) VALUES (?, ?, ? )", (name, topic, level))
    conn.commit()
    conn.close()

def get_user_preferences(name):
    conn= sqlite3.connect('users.db')
    c= conn.cursor()
    c.execute('select topic, level from users where name= ? order by rowid DESC LIMIT 1', (name,))
    result= c.fetchone()
    conn.close()
    return result
def generate_questions(topic, level, n_questions):
    prompt= prompt_template.format(topic= topic, level= level, n_questions= n_questions)
    response = model.invoke(prompt)
    return response.content.strip()

# Streamlit app
st.title("Personalized Learning Assistant")
st.write("Enter your name, topic and number of questions you need to test your Understanding in the certain topic.")

init_db() # initialise database

with st.form("user_form"):
    name= st.text_input("Enter the Name: ")
    # check for existing preferences
    preferences= get_user_preferences(name) if name else None

    topic= st.text_input("Enter the topic: ")
    level= st.slider("Level of difficulty from 1 to 10: ",min_value=1, max_value=10)
    n_questions= st.slider("Select the no of questions you want", min_value=1, max_value= 10)
    submit_button= st.form_submit_button("Generate Questions")

# Process form submission
if submit_button:
    if not name or not topic or not level:
        st.error("Please fill in all fields.")
    else:
        try:
            # Generate and display summary
            questions = generate_questions(topic, level, n_questions)
            st.subheader(f"Questions for {topic} for level {level}.")
            st.write(questions)

            # Save preferences
            save_user_preferences(name, topic, level)
            st.success(f"Try to answer the questions above,if you can great otherwise please go through the topics. Best of luck {name}\n(topic: {topic}, level: {level})!")

            # Reset new_preferences flag
            st.session_state["new_preferences"] = False
        except Exception as e:
            st.error(f"An error occurred: {e}")

# # Optional: Display all stored preferences
# if st.button("View Saved Preferences"):
#     conn = sqlite3.connect("users.db")
#     c = conn.cursor()
#     c.execute("SELECT * FROM users")
#     st.subheader("All Saved Preferences")
#     for row in c.fetchall():
#         st.write(row)
#     conn.close()



#
# # test the function
# if __name__ == '__main__':
#     init_db()
#     print("Welcome to the AI study assistant, let's top the marks")
#     name= input("Enter your name: ")
#     topic= input("Enter topic: ")
#     level= int(input("Enter level on scale of 1 to 10: "))
#     try:
#         summary= generate_summary(topic, level)
#         print(f"\n Try to answer the question this tells your understanding\n{summary}")
#
#         #save user preferences
#         save_user_preferences(name, topic, level)
#         print("Memory has been updated")
#     except Exception as e:
#         print(f"Check the error occurred{e}")
