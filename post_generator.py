from llm_helper import llm
from few_shot import FewShotPosts
import re

few_shot = FewShotPosts()


def strip_leading_markers(s: str) -> str:
    """Remove common list markers and simple labels from each line.

    This is a fallback cleanup for LLM outputs that still include bullets
    or section labels like 'Hook:', 'Body:', 'CTA:' or 'Hashtags:'.
    Hashtag content is left intact.
    """
    out_lines = []
    for l in s.splitlines():
        cleaned = re.sub(r'^[\s\u2022\-\*\u25E6\u25AA\u25CF\•]+', '', l).strip()
        cleaned = re.sub(r'^(Hook:|Body:|CTA:|Hashtags?:)\s*', '', cleaned, flags=re.IGNORECASE)
        out_lines.append(cleaned)
    return '\n'.join(out_lines)


def extract_labeled_sections(text: str):
    """Attempt to extract labeled Hook/Body/CTA/Hashtags sections from text.

    Returns tuple (hook, body, cta, hashtag_list) or None if not found.
    """
    hook = re.search(r"(?:^|\n)[\s\u2022\-\*]*Hook:\s*(.*)", text, re.IGNORECASE)
    body = re.search(r"(?:^|\n)[\s\u2022\-\*]*Body:\s*(.*)", text, re.IGNORECASE)
    cta = re.search(r"(?:^|\n)[\s\u2022\-\*]*CTA:\s*(.*)", text, re.IGNORECASE)
    hashtags = re.search(r"(?:^|\n)[\s\u2022\-\*]*Hashtags?:\s*(.*)", text, re.IGNORECASE)

    if not (hook or body or cta or hashtags):
        return None

    h = hook.group(1).strip() if hook else ''
    b = body.group(1).strip() if body else ''
    c = cta.group(1).strip() if cta else ''
    tags = []
    if hashtags:
        tags = re.findall(r"#\w+", hashtags.group(1))
    return (h, b, c, tags)


def count_nonempty_lines(s: str) -> int:
    return len([l for l in s.splitlines() if l.strip()])


def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


def generate_post(length, language, tag):
    prompt = get_prompt(length, language, tag)
    response = llm.invoke(prompt)
    text = response.content
    # First try extracting labeled sections
    labeled = extract_labeled_sections(text)
    if labeled:
        hook, body, cta, tags = labeled
        parts = [p for p in (hook, body, cta) if p]
        final = "\n\n".join(parts)
        if tags:
            final = final + "\n\n" + ' '.join(tags[:2])
        return final

    # enforce length via simple retry: if lines not in requested range, ask model to adjust
    if length == "Short":
        min_lines, max_lines = 1, 5
    elif length == "Medium":
        min_lines, max_lines = 6, 10
    else:
        min_lines, max_lines = 11, 15

    lines_count = count_nonempty_lines(text)
    retries = 0
    max_retries = 2
    while (lines_count < min_lines or lines_count > max_lines) and retries < max_retries:
        # ask model to adjust only, include original text for reference
        adjust_prompt = f"The post below does not meet the requested total line count ({min_lines}-{max_lines}).\n\nOriginal post:\n" + text + f"\n\nPlease return a revised version that meets the requested {min_lines}-{max_lines} total lines, keeping the same meaning and tone. Return only the revised post text."
        response = llm.invoke(adjust_prompt)
        text = response.content
        lines_count = count_nonempty_lines(text)
        retries += 1

    # Final cleanup: strip markers and parse paragraphs
    cleaned = strip_leading_markers(text)
    tags = re.findall(r"#\w+", cleaned)
    body_text = re.sub(r"(?:\s|^)(#\w+)(?=\s|$)", " ", cleaned).strip()
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body_text) if p.strip()]

    if len(paragraphs) >= 3:
        final = "\n\n".join(paragraphs[:3])
        if tags:
            final += "\n\n" + ' '.join(tags[:2])
        return final

    if len(paragraphs) == 2:
        final = "\n\n".join(paragraphs)
        if tags:
            final += "\n\n" + ' '.join(tags[:2])
        return final

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', body_text) if s.strip()]
    if len(sentences) >= 3:
        final = "\n\n".join([sentences[0], sentences[1], ' '.join(sentences[2:])])
        if tags:
            final += "\n\n" + ' '.join(tags[:2])
        return final

    if len(sentences) == 2:
        final = "\n\n".join(sentences)
        if tags:
            final += "\n\n" + ' '.join(tags[:2])
        return final

    final = body_text
    if tags and not re.search(r"(?m)^\s*#\w+(?:\s+#\w+)*\s*$", body_text):
        final = final.rstrip() + "\n\n" + ' '.join(tags[:2])
    return final


def get_prompt(length, language, tag):
    length_str = get_length_str(length)

    # map to numeric line ranges for enforcement
    if length == "Short":
        min_lines, max_lines = 1, 5
    elif length == "Medium":
        min_lines, max_lines = 6, 10
    else:
        min_lines, max_lines = 11, 15

    template = f"""You are a skilled LinkedIn copywriter. Generate ONE LinkedIn post only, following these strict rules (no extra commentary):

Topic: {tag}
Length: {length_str}
Language: {language}  (If 'Hinglish' mix Hindi words in Latin script.)
Tone: professional, concise, friendly.
Style: short crisp sentences, actionable.

Output FORMAT (exact):
- Hook: one short attention-grabbing sentence (<=25 words).
- Body: 1–2 supporting sentences with practical advice.
- CTA: one question prompting replies or resource-sharing.
- Hashtags: a final line with exactly 2 relevant hashtags (each starting with '#').

Strict rules:
- RETURN plain text only. Do NOT include labels like "Hook:", "Body:", "CTA:", or "Hashtags:".
- Do NOT use bullets, list markers, numbering, or decorative characters (no •, -, *, 1., a), etc.).
- Separate Hook, Body, CTA, and Hashtags with a single blank line between each section (four paragraphs total).
- The final line must contain exactly 2 hashtags only (e.g., "#Tag1 #Tag2").

Length requirement: the *total* post must be between {min_lines} and {max_lines} lines (counting each separate line/paragraph). Use line breaks to separate Hook, Body, CTA and Hashtags. Do NOT include extra lines.

If you cannot follow these rules exactly, reply only with: FAIL
"""

    # Add examples for few-shot guidance
    examples_df = few_shot.get_filtered_posts(length, language, tag)
    examples = examples_df.to_dict(orient='records') if examples_df is not None else []

    if len(examples) > 0:
        template += "\n\nUse the writing style of these examples (do not copy their content):"

    added = 0
    for post in examples:
        text = post.get('text', '').strip()
        if not text:
            continue
        template += f"\n\nExample {added+1}:\n{text}"
        added += 1
        if added == 2:
            break

    template += "\n\nGenerate the post now following the format exactly. If you cannot follow the rules, reply only with: FAIL"
    return template


if __name__ == "__main__":
    print(get_prompt("Short", "English", "Career Advice"))
