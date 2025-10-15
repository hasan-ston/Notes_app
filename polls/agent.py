from typing import TypedDict
from langgraph.graph import StateGraph, END
from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Define the state that flows through the agent
class AgentState(TypedDict):
    document_text: str
    questions: list
    best_questions: list
    quality_score: int
    best_score: int
    attempts: int


def generate_questions_node(state: AgentState):
    """Generate questions from document text"""
    print(f"\n🤖 AGENT: Generating questions (Attempt #{state['attempts'] + 1})...")

    prompt = f"""Generate 5 quiz questions with answers from this text:
    {state['document_text']}

    Format each as:
    Q: [question]
    A: [answer]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Parse response
    parts = response.text.split("Q: ")
    qa_pairs = []

    for part in parts:
        if "A: " in part:
            question_and_answer = part.split("A: ")
            question = question_and_answer[0].strip()
            answer = question_and_answer[1].strip()
            qa_pairs.append({'question': question, 'answer': answer})

    print(f"✅ Generated {len(qa_pairs)} questions")

    return {
        "questions": qa_pairs,
        "attempts": state["attempts"] + 1
    }


def evaluate_quality_node(state: AgentState):
    """Evaluate if questions are good enough"""
    print(f"\n🔍 AGENT: Evaluating question quality...")

    questions_text = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in state['questions']])

    eval_prompt = f"""Evaluate these quiz questions on a scale of 1-10...

    Questions:
    {questions_text}

    Respond with ONLY a number from 1-10.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=eval_prompt
    )

    try:
        score = int(response.text.strip())
    except:
        score = 7

    print(f"📊 Quality Score: {score}/10")

    # NEW: Keep track of best questions
    best_score = state.get("best_score", 0)
    if score > best_score:
        print(f"🎯 New best score! Saving these questions.")
        return {
            "quality_score": score,
            "best_score": score,
            "best_questions": state["questions"]
        }
    else:
        print(f"📉 Score lower than best ({best_score}/10). Keeping previous best.")
        return {
            "quality_score": score
        }

def should_regenerate(state: AgentState):
    """Decision: regenerate or finish?"""
    # If quality is good enough, finish
    if state["quality_score"] >= 7:
        print(f"✅ AGENT DECISION: Quality acceptable ({state['quality_score']}/10). Finishing!")
        return "finish"

    # If quality is bad but we can try again, regenerate
    if state["attempts"] < 3:
        print(f"❌ AGENT DECISION: Quality too low ({state['quality_score']}/10). Regenerating...")
        return "regenerate"

    # Quality is bad AND we're out of attempts - finish anyway but log it
    print(f"⚠️ AGENT DECISION: Quality still low ({state['quality_score']}/10) but max attempts reached. Using best available.")
    return "finish"


def create_agent_graph():
    """Build the agent workflow graph"""

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("generate", generate_questions_node)
    workflow.add_node("evaluate", evaluate_quality_node)

    # Set entry point
    workflow.set_entry_point("generate")

    # Add edges
    workflow.add_edge("generate", "evaluate")

    # Add conditional edge (the decision point!)
    workflow.add_conditional_edges(
        "evaluate",
        should_regenerate,
        {
            "regenerate": "generate",  # Loop back
            "finish": END  # Stop here
        }
    )

    # Compile the graph
    return workflow.compile()