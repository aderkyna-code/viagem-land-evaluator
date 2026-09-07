# Poznámky k iteracím promptu

### Iterace 1: Základní taxonomie a strukturovaný výstup
* **Cíl:** Přejít z nestrukturovaného textu na validní JSON se schématem (`KOUPIT` / `PROVĚŘIT` / `ZAMÍTNOUT`).
* **Výsledek:** Model generuje strojově zpracovatelný JSON a správně odděluje klíčové faktory od doporučení.

---

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

---

### Iterace 3: Zpřesnění obchodní logiky a kalibrace parametrů (v2 promptu)

Na základě zjištěných diskrepancí z prvního testovacího běhu (Iterace 2) byla provedena systémová úprava promptu zaměřená na odstranění falešně negativních výsledků a zjemnění definice STOP-faktorů.

#### 1. Provedené změny v promptu:
* **Normalizace zemědělského pachtu:** 
  Do systémové role bylo explicitně přidáno pravidlo: *„Běžný zemědělský pacht (nájemní smlouva se zemědělcem) u orné půdy v LPIS je standardní stav a NENÍ důvodem k zařazení do PROVĚŘIT.“* Tím byl eliminován přehnaně opatrný verdikt u bezrizikových zemědělských parcel.
* **Diferenciace exekučních plomb:** 
  Původní tvrdý STOP-faktor *„exekuční plomba na LV“* byl rozdělen. U běžné orné či lesní půdy zůstává fatální stopkou, avšak u stavebních parcel (plochy bydlení BI v ÚP) byl přesunut do kategorie `PROVĚŘIT`. Důvodem je vysoká přidaná hodnota odkupu problémové pohledávky či nákupu z dražby pod tržní cenou.
* **Striktní ošetření chybějících dat:** 
  Potvrzeno povinné mapování chybějících atributů na text *„Neuvedeno v datech“* s automatickým posunem do `PROVĚŘIT` u neúplných záznamů.

#### 2. Výsledky po re-testu (v2 promptu):
* **Starý Kolín (Case 1 – Happy path):** 
  * *Před úpravou:* `PROVĚŘIT` (kvůli existenci pachtu a neověřenému ÚP).
  * *Po úpravě:* `KOUPIT` (Riziko: 1, Likvidita: 9). Model správně vyhodnotil pacht jako běžnou provozní záležitost a doporučil okamžitý výkup.
* **Srbsko u Karlštejna (Case 2 – Přírodní limity):** 
  * *Výsledek:* Stabilně `ZAMÍTNOUT` (Riziko: 10, Likvidita: 1). Tvrdé STOP-faktory (Q20 + CHKO I + absence cesty) spolehlivě zafungovaly.
* **Říčany u Prahy (Case 3 – Právní vada vs. Rozvoj):** 
  * *Před úpravou:* `ZAMÍTNOUT` (kvůli platinové stopce na jakoukoliv plombu).
  * *Po úpravě:* `PROVĚŘIT` (Riziko: 7, Likvidita: 8). Model rozpoznal vysoký stavební potenciál lokality a doporučil kontaktovat exekutora/spoluvlastníka pro konsolidaci podílu.
* **Dolní Břežany (Case 4 – Missing data stresstest):** 
  * *Výsledek:* Stabilně `PROVĚŘIT` (Riziko: 9–10, Likvidita: 1–3). Model odmítl halucinovat čistý stav a striktně vyžaduje dodání chybějících podkladů.

#### 3. Závěr z iterace:
Prompt ve verzi 2 dosáhl **100% shody v kategorických doporučeních (`doporuceni`)** napříč celým benchmarkem. Drobné odchylky zůstaly pouze v numerických škálách (1–10), což potvrzuje nutnost v produkčním prostředí počítat přesná finanční a riziková skóre deterministicky mimo samotné LLM.

