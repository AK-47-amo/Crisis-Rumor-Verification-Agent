# 🛡️ Crisis Rumor Verification Agent

AI-powered disaster message analysis and verification system that combines **LLM feature extraction**, **ML classification**, and **rule-based risk scoring** to help users identify potential misinformation during crises.

---

## ✨ Features

- **LLM Analysis** — Extracts crisis type, location, urgency, source, and evidence using Groq (Llama 3.1)
- **ML Classification** — TF-IDF + Logistic Regression trained on Kaggle Disaster Tweets
- **Risk Scoring** — Rule-based 0–100 score with breakdown
- **Safe Recommendations** — Deterministic guidance with built-in disclaimers
- **Polished UI** — Dark-themed Streamlit dashboard with interactive risk gauge

---

## 🏗️ Architecture

```
app.py  →  pipeline.py  →  ┌─ llm_analyzer.py
                            ├─ ml_classifier.py
                            ├─ risk_scorer.py
                            └─ recommendation.py
```

All modules communicate via typed dataclasses defined in `models.py`.

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd "IIT Project2"
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Download Training Data

Download `train.csv` from the [Kaggle Disaster Tweets](https://www.kaggle.com/c/nlp-getting-started/data) competition and place it in the `data/` directory.

### 4. Train the ML Model

```bash
python train_model.py
```

### 5. Run the App

```bash
streamlit run app.py
```

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI entry point |
| `pipeline.py` | Orchestrator — wires all modules |
| `llm_analyzer.py` | Groq LLM feature extraction |
| `ml_classifier.py` | ML classifier (TF-IDF + LogReg) |
| `train_model.py` | One-time model training script |
| `risk_scorer.py` | Rule-based risk scoring (0–100) |
| `recommendation.py` | Safe recommendation generator |
| `models.py` | Shared dataclasses |
| `config.py` | Configuration & constants |
| `utils.py` | Text preprocessing utilities |

---

## 🔑 API Key

Get a free Groq API key at [Groq Console](https://console.groq.com/keys).

> **Note:** The app works without a Groq key using a keyword-based fallback, but LLM analysis will be less accurate.

---

## 📊 Model Performance

The TF-IDF + Logistic Regression model typically achieves:
- **Accuracy:** ~80%
- **F1 Score:** ~78%

on the Kaggle Disaster Tweets test split.

---

## ⚠️ Disclaimer

This is an automated assessment tool for educational purposes. Always verify crisis information with official sources before sharing or acting on it.
