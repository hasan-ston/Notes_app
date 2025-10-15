from django.shortcuts import render, redirect
from .models import Note_set, Questions
from .notes_ai import generate_questions
from llama_index.core import SimpleDirectoryReader

def index(request): # Request is sent by user
    note_set = Note_set.objects.all()
    dict = {
        'note_set': note_set
    }
    return render(request, "polls/home.html", dict)

def note_detail(request, id):
    note_set = Note_set.objects.get(id=id)
    questions = Questions.objects.filter(note_set=note_set)
    dict = {
        'note_set': note_set,
        'questions': questions
    }
    return render(request, "polls/details.html", dict)


def generate_questions_view(request, id):
    note_set = Note_set.objects.get(id=id)

    # text_content = note_set.content.read().decode('utf-8')
    Questions.objects.filter(note_set=note_set).delete()
    file_path = note_set.content.path

    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    text_content = documents[0].text

    from .agent import create_agent_graph
    agent = create_agent_graph()
    result = agent.invoke({
        "document_text": text_content,
        "questions": [],
        "quality_score": 0,
        "attempts": 0
    })

    # Generate questions using AI
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