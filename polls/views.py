import json
import os
import tempfile

import pymupdf
import requests
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from .models import Note_set, Questions


def index(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        uploaded_file = request.FILES.get("content")
        if not title or not uploaded_file:
            messages.error(request, "Title and file are required to create a flashcard set.")
        else:
            Note_set.objects.create(title=title, content=uploaded_file)
            messages.success(request, "Note uploaded. You can now generate flashcards.")
        return redirect("home")

    note_set = Note_set.objects.all()
    context = {
        'note_set': note_set
    }
    return render(request, "polls/home.html", context)


def note_detail(request, id):
    note_set = get_object_or_404(Note_set, id=id)
    questions = Questions.objects.filter(note_set=note_set)
    context = {
        'note_set': note_set,
        'questions': questions
    }
    return render(request, "polls/details.html", context)


def _extract_text_from_path(file_path: str) -> str:
    """Extract text from txt or pdf paths, with a best-effort OCR fallback."""
    extracted_text = ""
    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()
    else:
        doc = pymupdf.open(file_path)
        for page in doc:
            try:
                textpage = page.get_textpage_ocr()
                extracted_text += page.get_text(textpage=textpage)
            except RuntimeError:
                # Fallback when Tesseract OCR is unavailable; still use PyMuPDF text extraction.
                extracted_text += page.get_text()
        doc.close()
    return extracted_text


def _generate_questions_from_text(extracted_text: str):
    """Run the agent and return the best question set."""
    from .agent import create_agent_graph

    agent = create_agent_graph()
    result = agent.invoke(
        {
            "document_text": extracted_text,
            "questions": [],
            "quality_score": 0,
            "attempts": 0,
        }
    )
    return result.get("best_questions", [])


def generate_questions_view(request, id):
    note_set = get_object_or_404(Note_set, id=id)

    file_path = note_set.content.path
    extracted_text = _extract_text_from_path(file_path)

    if not extracted_text.strip():
        messages.error(request, "Could not read text from the uploaded note. For scanned PDFs, install Tesseract or upload a text PDF/TXT file.")
        return redirect('details', id=id)

    try:
        best_questions = _generate_questions_from_text(extracted_text)
    except Exception as exc:
        messages.error(request, f"Generating flashcards failed: {exc}")
        return redirect('details', id=id)

    # Replace old questions only if generation succeeded
    with transaction.atomic():
        Questions.objects.filter(note_set=note_set).delete()
        for qa in best_questions:
            Questions.objects.create(
                note_set=note_set,
                question_text=qa['question'],
                answer_text=qa['answer']
            )
    messages.success(request, "Flashcards refreshed.")
    return redirect('details', id=id)


@require_POST
def toggle_review(request, question_id):
    question = get_object_or_404(Questions, id=question_id)
    question.reviewed = not question.reviewed
    question.save(update_fields=['reviewed'])
    return redirect('details', id=question.note_set.id)


def _download_file_to_temp(url: str) -> str:
    """Download a remote file to a temp path and return it."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        resp = requests.get(url, stream=True, timeout=20)
        resp.raise_for_status()
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        return tmp.name


def _require_api_key(request):
    expected = settings.NOTES_API_KEY
    provided = request.headers.get("X-Api-Key") or request.headers.get("Authorization")
    if expected and provided != expected:
        return False
    return True


@csrf_exempt
@require_http_methods(["POST"])
def api_generate_questions(request):
    """API endpoint to generate Q&A pairs from text, a note_id, an uploaded file, or a remote file URL."""
    if not _require_api_key(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    payload = {}
    if request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

    note_id = payload.get("note_id") or request.POST.get("note_id")
    text_content = payload.get("text") or request.POST.get("text")
    file_url = payload.get("file_url")
    uploaded_file = request.FILES.get("file")

    temp_path = None
    try:
        if note_id:
            note_set = get_object_or_404(Note_set, id=note_id)
            source_path = note_set.content.path
            extracted_text = _extract_text_from_path(source_path)
        elif uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name
            extracted_text = _extract_text_from_path(temp_path)
        elif file_url:
            try:
                temp_path = _download_file_to_temp(file_url)
            except Exception as exc:
                return JsonResponse({"error": f"Failed to fetch file: {exc}"}, status=400)
            extracted_text = _extract_text_from_path(temp_path)
        elif text_content:
            extracted_text = text_content
        else:
            return JsonResponse({"error": "Provide note_id, file, file_url, or text"}, status=400)

        if not extracted_text.strip():
            return JsonResponse({"error": "No text content could be read"}, status=400)

        questions = _generate_questions_from_text(extracted_text)
        return JsonResponse({"questions": questions})
    except Exception as exc:
        return JsonResponse({"error": f"Generation failed: {exc}"}, status=500)
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

# The details view does the following:
# Gets the id as an argument.
# Uses the id to locate the correct record in the Note_set table.
# loads the details.html template.
# Creates an object containing the note_set.
# Sends the object to the template.
# Outputs the HTML that is rendered by the template.
