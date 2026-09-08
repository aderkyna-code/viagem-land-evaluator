import json
import os
import sys

def evaluate_parcel(parcel_text: str, prompt_path: str = "src/prompt.txt") -> dict:
    """
    Odešle data o parcele na LLM API s načteným systémovým promptem
    a vrátí validovaný výsledek jako Python slovník (JSON).
    """
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Soubor s promptem nebyl nalezen: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Vyhodnoť tuto parcelu:\n{parcel_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    elif gemini_key:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"Vyhodnoť tuto parcelu:\n{parcel_text}",
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )
        return json.loads(response.text)

    else:
        raise ValueError(
            "Nenalezen žádný API klíč. Nastav buď proměnnou prostředí OPENAI_API_KEY, nebo GEMINI_API_KEY."
        )

if __name__ == "__main__":
    sample_input = (
        "KÚ: Starý Kolín (754714), parcela č. 852/12, výměra 18 420 m2. "
        "Druh pozemku: Orná půda. Vlastnictví: 1/1, čisté LV bez věcných břemen a zástav. "
        "Přístup: přímo z obecní komunikace. LPIS: aktivní pacht, orná půda. "
        "Ochrana přírody a záplavy: mimo záplavová území, bez CHKO/Natura 2000."
    )

    print("Spouštím evaluaci vzorové parcely...")
    try:
        result = evaluate_parcel(sample_input)
        print("\nVýsledek evaluace:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Chyba při běhu evaluace: {e}", file=sys.stderr)
