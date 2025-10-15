# AI Study Notes Generator 📚

An AI-powered web application that automatically generates quiz questions from uploaded study notes using agentic AI workflows. Built with Django, LangGraph, and Google's Gemini API.

## 🎯 Features

- **Smart Document Processing**: Upload PDFs, Word docs (.docx), or text files
- **OCR Support**: Extracts text from scanned documents and images using PyMuPDF
- **Agentic Question Generation**: AI agent generates questions, evaluates quality, and regenerates if needed
- **Self-Improving**: Agent iteratively refines questions (up to 3 attempts) until quality threshold is met
- **Quality Tracking**: Keeps the best set of questions across multiple generation attempts
- **Modern UI**: Clean, responsive interface built with Tailwind CSS

## 🤖 What Makes This "Agentic"?

Unlike simple API calls, this project implements true agent behavior:

1. **Goal-Oriented**: Agent has a clear objective (generate high-quality questions)
2. **Decision-Making**: Evaluates its own output and decides whether to regenerate
3. **Iterative Improvement**: Can loop up to 3 times to improve question quality
4. **State Management**: Tracks best questions and scores across attempts
5. **Conditional Workflow**: Uses LangGraph to create decision trees, not linear chains

## 🛠️ Tech Stack

**Backend:**
- Django 5.2.7
- Python 3.13

**AI/ML:**
- Google Gemini 2.5 Flash (LLM)
- LangGraph (Agent framework)
- LlamaIndex (Document loading)

**Document Processing:**
- PyMuPDF (OCR for scanned PDFs)
- LlamaIndex SimpleDirectoryReader (Multi-format support)

**Frontend:**
- Tailwind CSS
- Django Templates

## 📋 Prerequisites

- Python 3.13+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- pip and virtualenv

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/hasan-ston/Notes_app
cd Notes_app
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django google-generativeai langgraph langchain-google-genai langchain-core llama-index llama-index-readers-file pymupdf
```

4. **Configure API Key**

Add your Gemini API key to `todo_app/settings.py`:
```python
GEMINI_API_KEY = "your_api_key_here"
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (for admin access)**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to use the app!

## 📖 Usage

### Uploading Notes

1. Go to `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Click "Note_sets" → "Add Note_set"
4. Enter a title and upload your document (PDF, DOCX, or TXT)
5. Save

### Generating Questions

1. Go to the home page (`/`)
2. Click on a note set
3. Click "Generate Q&A" button
4. Watch the terminal to see the agent working:
   - Generating questions
   - Evaluating quality
   - Regenerating if score < 7/10
   - Keeping best questions across attempts

## 🧠 How the Agent Works

### Agent Workflow

```
START
  ↓
[Generate Questions] (Attempt #1)
  ↓
[Evaluate Quality] → Score: 6/10
  ↓
Is score ≥ 7 AND attempts < 3?
  ↓ No
[Regenerate Questions] (Attempt #2)
  ↓
[Evaluate Quality] → Score: 8/10
  ↓ Yes
[Save Best Questions]
  ↓
END
```

### Agent State

The agent maintains state across iterations:
```python
{
    "document_text": "extracted content",
    "questions": [current questions],
    "best_questions": [highest scoring questions],
    "quality_score": 8,
    "best_score": 8,
    "attempts": 2
}
```

### Decision Logic

- **Quality Threshold**: Questions must score ≥7/10 to be accepted
- **Max Attempts**: Agent tries up to 3 times to generate acceptable questions
- **Best Tracking**: Even if later attempts score lower, the best questions from any attempt are saved

## 📁 Project Structure

```
mytasks/
├── polls/                    # Main Django app
│   ├── models.py            # Note_set and Questions models
│   ├── views.py             # View logic + file processing
│   ├── agent.py             # LangGraph agent workflow
│   ├── urls.py              # URL routing
│   └── templates/
│       └── polls/
│           ├── home.html    # List all note sets
│           └── details.html # View questions for a note set
├── todo_app/                # Django project settings
│   ├── settings.py          # Configuration + API key
│   └── urls.py              # Root URL config
└── manage.py
```

## 🎓 Key Learning Resources

- **LangGraph (Agent Framework):** [Official Tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- **PyMuPDF (OCR):** [Text Extraction Docs](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)
- **LlamaIndex (Document Loading):** [Quickstart Guide](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/)
- **Agent AI Concepts:** [Building Effective Agents (Anthropic)](https://www.anthropic.com/news/building-effective-agents)

## 🔧 Configuration Options

### Adjust Quality Threshold

In `polls/agent.py`, modify the `should_regenerate` function:
```python
if state["quality_score"] >= 7:  # Change threshold here
```

### Change Max Attempts

```python
if state["attempts"] < 3:  # Change max attempts here
```

### Modify Question Count

In `polls/agent.py`, change the prompt:
```python
prompt = f"""Generate 5 quiz questions...  # Change number here
```

## 🐛 Troubleshooting

**"CSRF verification failed"**
- Make sure `{% csrf_token %}` is inside your form tags
- Try clearing browser cookies

**"That port is already in use"**
```bash
lsof -ti:8000 | xargs kill -9
```

**Agent takes too long**
- Reduce max attempts from 3 to 2
- Lower quality threshold from 7 to 6
- Use faster model: `gemini-1.5-flash`

**OCR not extracting text**
- Ensure PyMuPDF is installed: `pip install pymupdf`
- Check if PDF is actually scanned (not text-based)
- Try with a clearer scan

## 🚀 Future Enhancements

- [ ] Add file upload directly on homepage (no admin needed)
- [ ] Implement flashcard mode (hide/show answers)
- [ ] Add "Mark as Reviewed" functionality
- [ ] Support for handwritten notes via vision models
- [ ] Difficulty level selection (easy/medium/hard)
- [ ] Export questions to Anki/Quizlet
- [ ] Multi-user support with authentication


## 👤 Author

Built by a first-year undergraduate student learning Django and AI integration.

## 🙏 Acknowledgments

- Google Gemini for the LLM API
- LangChain team for LangGraph framework
- Django community for excellent documentation

---

**Note**: This is a development project. For production use, implement proper environment variable management, error handling, and security measures.
