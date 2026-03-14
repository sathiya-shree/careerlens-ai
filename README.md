
# 🚀 CareerLens AI

### Intelligent Resume Analyzer using AI & NLP

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-red)
![AI](https://img.shields.io/badge/AI-Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**CareerLens AI** is an AI-powered resume analysis platform that helps job seekers **analyze, improve, and optimize their resumes** using Natural Language Processing and Generative AI.

The tool extracts skills, analyzes resume content, and provides **AI-generated improvement suggestions** to help candidates align with industry expectations.

---

# 🌐 Live Demo

```
https://careerlens-ai.streamlit.app
```

Hosted using **Streamlit**.

---

# 🖥️ Screenshots

### Resume Upload

![Resume Upload](screenshots/upload.png)




### AI Analysis Dashboard
![Analysis Dashboard](screenshots/analysis.png)



### Skilss Chart
![Skills Chart](screenshots/skills_chart.png)



# ✨ Features

### 📄 Resume Upload

Supports multiple formats:

* PDF
* DOCX
* TXT
* Image resumes (PNG/JPG)

---

### 🧠 AI Resume Analysis

Uses **Google Gemini API** to:

* Evaluate resume structure
* Suggest improvements
* Identify missing information
* Recommend skill additions

---

### 🔍 OCR Resume Reading

Extracts text from image resumes using:

* **Tesseract OCR**
* **Pillow**

---

### 🧾 Skill Extraction with NLP

Uses **spaCy** to detect:

* Programming languages
* Tools & frameworks
* Professional skills

---

### 📊 Skill Visualization

Displays skill distribution using **Matplotlib** charts.

---

# 🏗️ Tech Stack

| Technology          | Purpose               |
| ------------------- | --------------------- |
| **Python**          | Core programming      |
| **Streamlit**       | Web application UI    |
| **spaCy**           | NLP skill extraction  |
| **Matplotlib**      | Data visualization    |
| **pdfplumber**      | PDF parsing           |
| **docx2txt**        | DOCX parsing          |
| **Tesseract OCR**   | Image text extraction |
| **Google Gemini API** | AI insights           |

---

# 📂 Project Structure

```
careerlens-ai
│
├── app.py
├── requirements.txt
├── packages.txt
│
├── screenshots
│    ├── upload.png
│    ├── analysis.png
│    └── skills_chart.png
│
└── .streamlit
     └── secrets.toml
```

---

# ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/sathiya-shree/careerlens-ai.git
cd careerlens-ai
```

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Install spaCy model

```bash
python -m spacy download en_core_web_sm
```

---

### 4️⃣ Add Gemini API Key

Create file:

```
.streamlit/secrets.toml
```

Add:

```
GEMINI_API_KEY="your_api_key"
```

---

### 5️⃣ Run the application

```bash
streamlit run app.py
```

Open:

```
http://localhost:8501
```

---

# 🚀 Deployment

The application can be deployed easily using:

* **Streamlit**
* **Render**
* **Railway**

Recommended for quick deployment: **Streamlit Cloud**.

---

# 🔐 Security

Sensitive information like API keys are stored securely using **Streamlit Secrets** and **not committed to GitHub**.

---

# 📈 Future Improvements

Planned enhancements:

* Resume **ATS score system**
* **Job description matching**
* **AI resume rewriting**
* **LinkedIn profile analyzer**
* Export **resume feedback report (PDF)**

---

# 👨‍💻 Author

GitHub:

```
https://github.com/sathiya-shree
```
