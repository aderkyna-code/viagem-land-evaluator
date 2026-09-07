# Poznámky k iteracím promptu

### Iterace 1: Základní taxonomie a strukturovaný výstup
* **Cíl:** Přejít z nestrukturovaného textu na validní JSON se schématem (`KOUPIT` / `PROVĚŘIT` / `ZAMÍTNOUT`).
* **Výsledek:** Model generuje strojově zpracovatelný JSON a správně odděluje klíčové faktory od doporučení.

___

### Iterace 2: Validace na benchmarku a identifikace hraničních stavů

#### 1. Starý Kolín (Case 1 – Happy Path): Falešně negativní výsledek (Over-caution)
* **Očekávání:** `KOUPIT`
* **Skutečný výstup:** `PROVĚŘIT` (skóre rizika: 3)
* **Příčina:** 
  1. Model detekoval nesoulad v kódu katastrálního území (754714 vs. reálný 755052).
  2. Prompt neobsahoval instrukci, jak nakládat se zemědělským pachtem. Model vyhodnotil standardní pacht jako překážku vyžadující prověření.
* **Úprava pro v2:** Přidat pravidlo: *„Běžný zemědělský pacht evidovaný v LPIS není u orné půdy překážkou nákupu a nezakládá status PROVĚŘIT, pokud je LV čisté.“*

#### 2. Srbsko u Karlštejna (Case 2 – Environmentální STOP-faktor)
* **Očekávání:** `ZAMÍTNOUT`
* **Skutečný výstup:** `ZAMÍTNOUT` (skóre rizika: 10, likvidita: 1)
* **Příčina:** Pravidla zafungovala přesně — kumulace aktivní záplavové zóny Q20, I. zóny CHKO a chybějícího přístupu vedla k okamžitému zamítnutí.

#### 3. Říčany u Prahy (Case 3 – Právní vada vs. Rozvojový potenciál)
* **Očekávání:** `PROVĚŘIT` (lukrativní stavební rezerva)
* **Skutečný výstup:** `ZAMÍTNOUT` (skóre rizika: 10, likvidita: 2)
* **Příčina:** Příliš striktní definice STOP-faktoru *„exekuční plomba na LV“*. Model ignoroval vysoký ziskový potenciál stavebního pozemku v ploše BI a vyhodnotil plombu jako absolutní stopku.
* **Úprava pro v2:** Upravit definici STOP-faktoru exekuce. Pozemky se stavebním potenciálem v územním plánu posuzovat v kategorii `PROVĚŘIT`, pokud lze uvažovat o oddlužení či výkupu v dražbě. Jako tvrdý STOP-faktor ponechat exekuci pouze u běžné zemědělské půdy bez rozvojového potenciálu.

#### 4. Dolní Břežany (Case 4 – Chybějící data a halucinace)
* **Očekávání:** `PROVĚŘIT` (skóre rizika: 6)
* **Skutečný výstup:** `PROVĚŘIT`
* **Příčina:** Pravidlo proti halucinacím zafungovalo. Model si nedomyslel čisté LV ani existenci komunikace a explicitně uvedl „Neuvedeno v datech“.
