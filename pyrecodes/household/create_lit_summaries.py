"""Script to generate literature summaries for household GPT agents.

Reads PDFs from a folder, calls GPT to extract 10 empirical findings per paper
about post-disaster household displacement, and saves them to a JSON file.

Usage:
    python -m pyrecodes.household.create_lit_summaries \
        --pdf_folder "Example 6/literature_for_households_pdfs" \
        --output_file pyrecodes/household/literature_summaries.json \
        --api_key_file ./openai_api_key.json
"""

import argparse
import json
from pathlib import Path

import pypdf

from pyrecodes.household.household_gpt_base import LLM

SUMMARY_PROMPT_TEMPLATE = (
    "You are a research assistant. The following is the full text of an academic paper. "
    "Extract exactly 10 empirical findings from this paper that are relevant to post-disaster "
    "household displacement and return decisions (e.g., what factors drive households to "
    "leave, stay, or return after a disaster). "
    "Return ONLY a JSON array of exactly 10 strings, one finding per element. "
    "Each finding must be a single, self-contained sentence in plain English. "
    "Do not include any explanation or text outside the JSON array.\n\n"
    "Paper text:\n{text}"
)

MAX_CHARS = 60_000


def extract_text(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    full_text = "\n".join(pages)
    return full_text[:MAX_CHARS]


def parse_findings(answer: str) -> list:
    """Extract a JSON array from GPT answer, stripping markdown code fences if present."""
    text = answer.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    findings = json.loads(text)
    if not isinstance(findings, list):
        raise ValueError(f"Expected a JSON array, got: {type(findings)}")
    return [str(f) for f in findings]


def summarize_paper(llm: LLM, pdf_path: Path) -> list:
    text = extract_text(pdf_path)
    prompt = [{"role": "user", "content": SUMMARY_PROMPT_TEMPLATE.format(text=text)}]
    for attempt in range(3):
        answer = llm.query_llm(prompt)
        try:
            return parse_findings(answer)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Attempt {attempt + 1} failed ({e}). Raw answer: {answer[:200]!r}")
    raise RuntimeError(f"Could not parse findings for {pdf_path.name} after 3 attempts.")


def build_summaries(pdf_folder: Path, llm: LLM) -> list:
    summaries = []
    for pdf_path in sorted(pdf_folder.glob("*.pdf")):
        print(f"Processing: {pdf_path.name}")
        findings = summarize_paper(llm, pdf_path)
        summaries.append({"paper": pdf_path.stem, "findings": findings})
        print(f"  -> {len(findings)} findings extracted.")
    return summaries


def save_summaries(summaries: list, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"Literature": summaries}, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(summaries)} summaries to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate literature summaries for household GPT agents.")
    parser.add_argument("--pdf_folder", default="Example 6/literature_for_households_pdfs", help="Folder containing PDF files.")
    parser.add_argument("--output_file", default="pyrecodes/household/literature_summaries.json", help="Output JSON file path.")
    parser.add_argument("--api_key_file", default="./openai_api_key.json", help="Path to OpenAI API key JSON file.")
    args = parser.parse_args()

    llm = LLM(api_key_filename=args.api_key_file, temperature=0.0)
    summaries = build_summaries(Path(args.pdf_folder), llm)
    save_summaries(summaries, Path(args.output_file))


if __name__ == "__main__":
    main()
