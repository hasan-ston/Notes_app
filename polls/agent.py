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

    prompt = f"""You are an expert educator creating comprehensive quiz questions.

CRITICAL REQUIREMENTS:
1. Read the ENTIRE document carefully before generating questions
2. Identify ALL major topics, concepts, and key points in the document
3. Generate questions that cover the FULL RANGE of material (beginning, middle, and end)
4. DO NOT focus only on the beginning or one section
5. Ensure questions test understanding of different concepts, not just one topic repeatedly

Document to analyze:
{state['document_text']}

Generate exactly 5 high-quality quiz questions that:
- Cover different sections of the material
- Test different concepts/topics from the document
- Range from basic recall to deeper understanding
- Are clear and unambiguous
- Have complete, accurate answers

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

    eval_prompt = f"""Evaluate these quiz questions based on:

COVERAGE (most important):
- Do questions cover different topics from the document?
- Are multiple sections/concepts represented?
- Or do all questions focus on just one small part?

QUALITY:
- Are questions clear and well-written?
- Are answers accurate and complete?
- Do questions test understanding, not just memorization?

Questions to evaluate:
{questions_text}

Rate from 1-10 where:
- 1-3: Poor coverage (focuses on one topic only) or very low quality
- 4-6: Partial coverage (misses major topics) or medium quality
- 7-8: Good coverage (hits most topics) and good quality
- 9-10: Excellent coverage (comprehensive) and excellent quality

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

    # Keep track of best questions
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