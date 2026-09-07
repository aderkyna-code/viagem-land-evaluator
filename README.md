# Viagem: LLM Evaluátor Parcel pro Výkup Pozemků

Tento projekt obsahuje návrh a implementaci LLM řešení pro automatizované vyhodnocování a strukturovaný scoring parcel pro účely výkupu ve společnosti Viagem.

## Klíčové vlastnosti řešení
- **Deterministická taxonomie:** Striktní kategorizace parcel do tří stavů: `KOUPIT` | `PROVĚŘIT` | `ZAMÍTNOUT`.
- **Garance výstupu:** Výstup je validní JSON se strukturovaným rozpadem rizik (právní vady, přístupnost, environmentální limity).
- **Ošetření hraničních případů:** Implementace tvrdých stop-faktorů (aktivní záplavové zóny, absence cesty, plomby na LV) a explicitní práce s neúplnými daty bez halucinací.

## Struktura projektu
- `src/prompt.txt` – Finální verze systémového promptu s definovanou JSON taxonomií.
- `notebooks/demo_evaluation.ipynb` – Interaktivní notebook demonstrující vyhodnocení na 4 testovacích parcelách.
- `data/test_cases.json` – Vstupy, očekávané a reálné výstupy testovacích scénářů (Happy path, Právní vada, Záplavy, Missing data).
- `docs/iterace.md` – Popis 3 fází vývoje promptu a odůvodnění změn.
- `docs/reflexe.md` – Analýza limitů LLM a návrh produkční GIS/Python pipeline.

## Rychlé spuštění
1. Klonování repozitáře:
   ```bash
   git clone [https://github.com/](https://github.com/)<tvoje-jmeno>/viagem-land-evaluator.git
   cd viagem-land-evaluator
