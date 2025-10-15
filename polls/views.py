from django.shortcuts import render, redirect
from .models import Note_set, Questions
import pymupdf


def index(request):
    note_set = Note_set.objects.all()
    context = {
        'note_set': note_set
    }
    return render(request, "polls/home.html", context)


def note_detail(request, id):
    note_set = Note_set.objects.get(id=id)
    questions = Questions.objects.filter(note_set=note_set)
    context = {
        'note_set': note_set,
        'questions': questions
    }
    return render(request, "polls/details.html", context)


def generate_questions_view(request, id):
    note_set = Note_set.objects.get(id=id)
    Questions.objects.filter(note_set=note_set).delete()

    file_path = note_set.content.path

    # Extract text from PDF using OCR
    extracted_text = ""
    doc = pymupdf.open(file_path)
    for page in doc:
        textpage = page.get_textpage_ocr()
        extracted_text += page.get_text(textpage=textpage)
    doc.close()

    # Generate questions using agent
    from .agent import create_agent_graph
    agent = create_agent_graph()
    result = agent.invoke({
        "document_text": extracted_text,
        "questions": [],
        "quality_score": 0,
        "attempts": 0
    })

    # Save generated questions
    for qa in result["best_questions"]:
        Questions.objects.create(
            note_set=note_set,
            question_text=qa['question'],
            answer_text=qa['answer']
        )

    return redirect('details', id=id)

# The details view does the following:
# Gets the id as an argument.
# Uses the id to locate the correct record in the Note_set table.
# loads the details.html template.
# Creates an object containing the note_set.
# Sends the object to the template.
# Outputs the HTML that is rendered by the template.