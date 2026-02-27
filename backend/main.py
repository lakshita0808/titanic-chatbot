import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

# ==========================================
# 1️⃣ Load Titanic Dataset
# ==========================================
# Make sure titanic.csv is inside backend folder
df = pd.read_csv("titanic.csv")

# ==========================================
# 2️⃣ Initialize LangChain LLM
# ==========================================
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0
)

# Create Pandas DataFrame Agent
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=False,
    allow_dangerous_code=True
)

# ==========================================
# 3️⃣ Initialize FastAPI
# ==========================================
app = FastAPI(title="Titanic Dataset Chat Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str


# ==========================================
# 4️⃣ Helper: Convert Matplotlib to Base64
# ==========================================
def convert_plot_to_base64(fig):
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return image_base64


# ==========================================
# 5️⃣ Auto Visualization Generator
# ==========================================
def generate_visualization(question: str):
    q = question.lower()

    # Histogram for Age
    if "histogram" in q or "distribution" in q:
        if "age" in q:
            fig, ax = plt.subplots()
            df["Age"].dropna().hist(bins=30, ax=ax)
            ax.set_title("Age Distribution")
            ax.set_xlabel("Age")
            ax.set_ylabel("Count")
            return convert_plot_to_base64(fig)

        if "fare" in q:
            fig, ax = plt.subplots()
            df["Fare"].dropna().hist(bins=30, ax=ax)
            ax.set_title("Fare Distribution")
            ax.set_xlabel("Fare")
            ax.set_ylabel("Count")
            return convert_plot_to_base64(fig)

    # Bar chart for Embarkation Port
    if "embark" in q or "port" in q:
        fig, ax = plt.subplots()
        df["Embarked"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Passengers per Embarkation Port")
        ax.set_xlabel("Port")
        ax.set_ylabel("Count")
        return convert_plot_to_base64(fig)

    # Gender pie chart
    if "male" in q or "female" in q or "gender" in q:
        fig, ax = plt.subplots()
        df["Sex"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_title("Gender Distribution")
        ax.set_ylabel("")
        return convert_plot_to_base64(fig)

    return None


# ==========================================
# 6️⃣ Main API Endpoint
# ==========================================
@app.post("/ask")
def ask_question(request: QuestionRequest):

    try:
        # Get LLM agent answer
        answer = agent.run(request.question)

        # Generate visualization if applicable
        plot_base64 = generate_visualization(request.question)

        return {
            "answer": answer,
            "plot": plot_base64
        }

    except Exception as e:
        return {
            "answer": f"Error processing question: {str(e)}",
            "plot": None
        }