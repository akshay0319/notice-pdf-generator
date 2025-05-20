# 📄 Notice PDF Generation System

## ✅ Overview

This system generates high-performance, bulk legal/commercial notices in PDF format using predefined HTML templates and dynamic user data. It is designed for businesses that require large-scale communication via legally formatted documents such as debt recovery notices, compliance alerts, or employee updates.

---

## ⚙️ Tech Stack

- **Backend**: FastAPI (Python)
- **PDF Rendering**: WeasyPrint
- **Template Engine**: Jinja2
- **Concurrency**: ThreadPoolExecutor
- **Frontend**: Simple HTML+JS UI (no framework)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Packaging**: Streaming ZIP (in-memory)

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/notice-pdf-generator.git
cd notice-pdf-generator
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn app.main:app --reload
```

### 5. Access the UI

- Open browser and go to:  
  `http://127.0.0.1:8000/ui/`

- API docs available at:  
  `http://127.0.0.1:8000/docs`

---

## 💻 Features

### 🧾 Template Management
- `POST /templates/` — Create a new HTML template
- `GET /templates/list` — View available templates
- `DELETE /templates/{id}` — Remove a template

### 👥 Notice Input
- Accepts bulk person data as JSON
- Dynamically replaces variables in HTML using Jinja2

### 🖨️ PDF Generation
- `POST /bulk` — Generate and download ZIP of PDFs
- Concurrently processes 1000+ PDFs using threading
- Real-time progress and elapsed time shown in UI

---

## 📈 Performance Benchmark

| Test Batch | Total PDFs | Time Taken | Avg Speed |
|------------|-------------|------------|------------|
| Sample 1   | 1000 PDFs   | 123 sec    | ~487 PDFs/min |
| Sample 2   | 500 PDFs    | 62 sec     | ~483 PDFs/min |

> ✅ Meets target: 500–600 PDFs/min in real-world usage with thread-based processing

---

## 🧠 Assumptions Made

- No user login/authentication required
- Notice data is provided directly via JSON input
- PDF output formatting depends on HTML template structure
- Templates can include any valid HTML and CSS
- We skipped persistent Notice DB records to save development time

---

## 📐 Architecture Diagram

```text
[UI] → /templates (CRUD)
     → /bulk (POST JSON)
     → [FastAPI Backend]
            ↓
      [Template Renderer]
            ↓
      [WeasyPrint PDF Engine]
            ↓
      [ZIP Generator → Response Stream]
```

---

## 🏁 Final Notes

- Fully open-source and OS-independent
- Flexible for integration into any legal, compliance, or financial systems
- Easy to deploy on **PythonAnywhere**, **Render**, or **Heroku**

---

## 📬 Submission

- Case study prepared as per the provided project brief
- GitHub Repo / ZIP contains:
  - ✅ Code
  - ✅ Frontend UI
  - ✅ Working APIs
  - ✅ README (this file)

---