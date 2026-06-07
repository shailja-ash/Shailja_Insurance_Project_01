"""
Simple rubric evaluator for Coverwise Insurance Chat Bot.
Compatible with Python 3.8 / 3.9.

Important idea:
- Do NOT compare the model response with gold_answer word-by-word.
- gold_answer is only a human reference.
- Score using expected fields, must_contain, and must_not_contain.

Run:
    python evaluate_coverwise_rubric.py

Required files in same folder:
    coverwise_prompt.md
    coverwise_eval_cases.json
    .env with OPENAI_API_KEY
"""

import json
from pathlib import Path
from typing import List, Literal, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError


load_dotenv()
client = OpenAI()

MODEL = "gpt-4o-mini"
PROMPT_FILE = "prompts/insurance_system_prompt.md"
TEST_FILE = "coverwise_eval_cases.json"
REPORT_FILE = "evaluation_report.json"


class InsuranceBotResponse(BaseModel):
    """Expected structured JSON from the chatbot."""

    answer_type: Literal[
        "recommendation",
        "comparison",
        "information",
        "clarifying_question",
        "out_of_scope",
    ]
    product_category: Literal["health", "term", "car", "home", "none"]
    greeting: str = Field(default="")
    final_response: str
    recommended_plan: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    coverage: Optional[str] = None
    premium: Optional[str] = None


def to_dict(model_object):
    """Support both Pydantic v1 and v2."""
    if hasattr(model_object, "model_dump"):
        return model_object.model_dump()
    return model_object.dict()


def clean(value):
    """Normalize text for loose matching."""
    if value is None:
        return ""
    return str(value).lower().strip()


def make_searchable_text(actual):
    """
    Build one text blob from all useful response fields.

    This avoids false failures like:
    - final_response has plan name
    - coverage is present in coverage field
    - premium is present in premium field
    - greeting is present in greeting field

    We should score the full structured answer, not only final_response.
    """
    parts = [
        actual.greeting,
        actual.final_response,
        actual.recommended_plan,
        actual.coverage,
        actual.premium,
        " ".join(actual.reasons),
    ]
    return clean(" ".join([str(x) for x in parts if x]))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def call_bot(system_prompt, user_question):
    """Call OpenAI and return validated Pydantic object."""

    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
        response_format=InsuranceBotResponse,
    )

    parsed = completion.choices[0].message.parsed

    if parsed is None:
        raise ValueError("Model did not return valid structured JSON.")

    # Explicit Pydantic validation for teaching clarity
    return InsuranceBotResponse(**to_dict(parsed))


def exact_or_empty(actual_value, expected_value):
    """If expected value exists, compare it. If not expected, pass."""
    if expected_value is None:
        return True
    return clean(actual_value) == clean(expected_value)


def score_case(case, actual=None, error=None):
    """
    Score one test case.

    Total = 10 points:
    1. Valid structured JSON
    2. Correct answer_type
    3. Correct product_category
    4. Correct recommended_plan, when expected
    5. Correct coverage, when expected
    6. Correct premium, when expected
    7. Must-contain words/phrases found anywhere in structured answer
    8. Must-not-contain words/phrases absent from structured answer
    9. Greeting rule followed
    10. Out-of-scope exact response rule, when applicable
    """

    expected = case.get("expected", {})

    result = {
        "id": case.get("id"),
        "test_area": case.get("test_area"),
        "query": case.get("query"),
        "gold_answer_reference_only": case.get("gold_answer"),
        "score": 0,
        "max_score": 10,
        "passed": False,
        "checks": {},
        "actual": None,
        "error": error,
    }

    if error is not None or actual is None:
        result["checks"]["valid_json"] = False
        return result

    actual_dict = to_dict(actual)
    result["actual"] = actual_dict

    searchable_text = make_searchable_text(actual)
    final_response = clean(actual.final_response)

    score = 0

    # 1. Valid structured JSON
    result["checks"]["valid_json"] = True
    score += 1

    # 2. answer_type
    ok = actual.answer_type == expected.get("answer_type")
    result["checks"]["answer_type"] = ok
    if ok:
        score += 1

    # 3. product_category
    ok = actual.product_category == expected.get("product_category")
    result["checks"]["product_category"] = ok
    if ok:
        score += 1

    # 4. recommended_plan
    ok = exact_or_empty(actual.recommended_plan, expected.get("recommended_plan"))
    result["checks"]["recommended_plan"] = ok
    if ok:
        score += 1

    # 5. coverage
    ok = exact_or_empty(actual.coverage, expected.get("coverage"))
    result["checks"]["coverage"] = ok
    if ok:
        score += 1

    # 6. premium
    ok = exact_or_empty(actual.premium, expected.get("premium"))
    result["checks"]["premium"] = ok
    if ok:
        score += 1

    # 7. must_contain anywhere in structured answer
    missing = []
    for phrase in expected.get("must_contain", []):
        if clean(phrase) not in searchable_text:
            missing.append(phrase)
    ok = len(missing) == 0
    result["checks"]["must_contain"] = ok
    result["checks"]["missing_phrases"] = missing
    if ok:
        score += 1

    # 8. must_not_contain anywhere in structured answer
    found_forbidden = []
    for phrase in expected.get("must_not_contain", []):
        if clean(phrase) in searchable_text:
            found_forbidden.append(phrase)
    ok = len(found_forbidden) == 0
    result["checks"]["must_not_contain"] = ok
    result["checks"]["forbidden_phrases_found"] = found_forbidden
    if ok:
        score += 1

    # 9. Greeting rule
    greeting_required = expected.get("greeting_required")
    if greeting_required is True:
        ok = "hello" in clean(actual.greeting) or "hello" in final_response
    elif greeting_required is False:
        ok = "hello" not in clean(actual.greeting) and "hello" not in final_response
    else:
        ok = True
    result["checks"]["greeting_rule"] = ok
    if ok:
        score += 1

    # 10. Out-of-scope exact rule
    if expected.get("answer_type") == "out_of_scope":
        ok = final_response == clean("Please ask questions about Coverwise Insurance products only.")
    else:
        ok = True
    result["checks"]["out_of_scope_exact_response"] = ok
    if ok:
        score += 1

    result["score"] = score
    result["passed"] = score == result["max_score"]
    return result


def main():
    system_prompt = Path(PROMPT_FILE).read_text(encoding="utf-8")
    test_cases = load_json(TEST_FILE)

    results = []

    for case in test_cases:
        print("Running:", case.get("id"), "-", case.get("query"))

        try:
            actual = call_bot(system_prompt, case["query"])
            result = score_case(case, actual=actual)
        except ValidationError as e:
            result = score_case(case, error="Pydantic validation error: " + str(e))
        except Exception as e:
            result = score_case(case, error=str(e))

        results.append(result)

    total_score = sum(r["score"] for r in results)
    max_score = sum(r["max_score"] for r in results)
    passed_count = sum(1 for r in results if r["passed"])

    report = {
        "note": "gold_answer is reference only. Scoring uses expected fields and rubric checks.",
        "total_cases": len(results),
        "passed_cases": passed_count,
        "failed_cases": len(results) - passed_count,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 2) if max_score else 0,
        "results": results,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\nEvaluation complete")
    print("Passed:", passed_count, "/", len(results))
    print("Score:", total_score, "/", max_score)
    print("Percentage:", report["percentage"], "%")
    print("Report saved to:", REPORT_FILE)


if __name__ == "__main__":
    main()
