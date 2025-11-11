# 🧠🤖 Text Humanizer API

**Text Humanizer** is an AI-powered microservice that transforms robotic, AI-generated, or overly formal text into smooth, natural, and human-like writing.  
It provides a flexible FastAPI backend integrated with **Gemini**, along with preprocessing and postprocessing layers for intelligent text normalization and quality scoring.

---

## Overview

The system processes text through a structured NLP pipeline:

1. User Input (text, tone)
2. Preprocessing (PII masking, normalization, scoring)
3. Prompt building (tone-aware)
4. Model execution (LangChain + Gemini)
5. Postprocessing (grammar correction, PII restore)
6. Final output returned to the user\

## Technologies Used

- FastAPI (backend framework)
- LangChain (LLM pipeline management)
- Gemini API (model backend for text rewriting)
- NLTK / spaCy / re (text cleaning, tokenization)
- textstat (readability scoring)
- language_tool_python (grammar correction)
- Uvicorn / Docker / AWS (deployment)

## Core Components

**Prompt Service**
- Builds tone-based prompts (`neutral`, `friendly`, `formal`).
- Default tone is neutral if not provided.

**Preprocessing**
- Cleans and normalizes text.
- Masks sensitive data (PII).
- Splits text into manageable chunks.

**Model Execution**
- Calls Gemini via Google SDK.
- Processes text in and pass down to Gemini.

**Postprocessing**
- Restores masked data.
- Corrects grammar and fluency.
- Merges output chunks coherently.

**Scoring**
- Calculates readability using Flesch Reading Ease, SMOG, and Coleman-Liau.

## API Endpoint

### POST /humanize

**Description:** Converts input text into natural human-like form.