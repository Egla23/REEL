# Multimodal AI Recommendation System

A complete Streamlit-based AI application that leverages the Google Gemini API to process multimodal user inputs—including text, image uploads, and digital sketches—to generate personalized recommendations. 

This system is designed as a direct multimodal recommendation engine, processing complex user intake without relying on a Retrieval-Augmented Generation (RAG) architecture.

## Repository Structure

The application is highly modularized for clean execution and easy scalability:

* `app.py`: The main Streamlit application entry point and core user interface.
* `bot.py`: Handles the core Google Gemini API integration and model interaction logic.
* `components.py`: Contains reusable UI modules and layout structures for the frontend interface.
* `prompts.py`: Stores the system instructions and structured prompt templates for the AI agent.
* `config.py`: Manages environment variables, model parameters, and global configuration settings.
* `utils.py`: Helper functions for data parsing, input processing, and other backend tasks.
* `style.css`: Custom stylesheet for refining the Streamlit visual experience.
* `links.csv`: A structured dataset containing the external links and metadata used to map and generate the final recommendations.
* `requirements.txt`: The required Python dependencies.

## Technical Stack
* **Frontend:** Streamlit, Custom CSS
* **AI/LLM Engine:** Google Gemini API (Multimodal Vision & Text capabilities)
* **Data Mapping:** Flat-file CSV (`links.csv`)
* **Language:** Python

## Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name

2. Install Dependencies
Install the required packages using pip:

Bash
pip install -r requirements.txt

4. Run the Application
streamlit run app.py
