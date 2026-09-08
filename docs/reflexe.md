# Reflexe: Limity řešení a budoucí směřování

Tato reflexe shrnuje zjištěné limity evaluátoru parcel postaveného na bázi systémového promptu a LLM (`gemini-3.6-flash`), identifikuje hraniční scénáře a navrhuje architekturu, kterou bych zvolila při dalším rozvoji projektu.

---

## 1. Kde prompt v současné podobě selhává

### A. Subjektivita a kalibrace numerického skórování (1–10)
* **Problém:** Jazykové modely nemají přirozenou matematickou kalibraci pro spojité škály. Rozdíl mezi rizikem 6/10 a 7/10 je v LLM často daný náhodností vzorkování (temperature) spíše než exaktním váženým výpočtem.
* **Projev:** U menšinového podílu 1/6 model udělil riziko 7/10, zatímco očekávaná hodnota byla 6/10. Klasifikace doporučení (`PROVĚŘIT`) byla správná, ale jemné nuance skóre mohou mezi běhy mírně kolísat.

### B. Práce s chybějícími a neúplnými daty (Asymetrie vstupu)
* **Problém:** Pokud vstupní nestrukturovaný text nezmíní klíčový parametr (např. v TC-005 a TC-006 nebyla uvedena existence záplavové zóny ani CHKO), prompt musí balancovat mezi dvěma riziky:
  1. *Halucinace* (model si domyslí, že pozemek není v záplavě).
  2. *Paralýza* (model odmítne pozemek vyhodnotit).
* **Současné chování:** Prompt byl vykalibrován tak, aby v takovém případě explicitně uvedl `"Neuvedeno v datech"` a navrhl dohledání jako další krok. Přesto se tím přenáší zátěž na lidského analytika.

### C. Geometrická a prostorová slepota (Spatial context)
* **Problém:** Textový model nedokáže z popisu *„přístup přes obecní parcelu“* nebo *„vedení VVN 110 kV přes střed“* spočítat reálný dopad na využitelnost půdy. Nevidí tvar parcely (nudle vs. ucelený lán), sklonitost terénu ani to, zda ochranné pásmo rozděluje parcelu na dvě neobhospodařovatelné poloviny.

### D. Závislost na kvalitě formulace vstupního textu
* **Problém:** Pokud vstup obsahuje protichůdná nebo právně nepřesná tvrzení (např. prodejce tvrdí „bez věcných břemen“, ale vzápětí zmíní „sloup vysokého napětí“), LLM může podlehnout přesvědčivosti prodejce a břemeno podhodnotit.

---

## 2. Co bych s více časem řešila jinak (Produkční architektura)

Čistý single-turn prompt je skvělý pro rychlý prototyping a filtraci, ale v produkčním prostředí Viagemu by neměl stát osamoceně. S větším časovým fondem bych systém rozšířila následujícím způsobem:

### 1. Hybridní architektura: Deterministická pravidla + LLM
* **Hard filters (kód):** Exekuce na LV, plomba probíhajícího řízení nebo nulový přístup by neměly být vyhodnocovány LLM. Jednoduchý Python skript s regulárními výrazy / databázovými pravidly může tyto parcely okamžitě označit jako `ZAMÍTNOUT` s nulovou latencí a 100% spolehlivostí.
* **LLM pouze na sémantiku:** Jazykový model by se soustředil pouze na interpretaci nestrukturovaných poznámek, smluvních ujednání pachtu a syntézu textového odůvodnění pro investora.

### 2. Integrace externích API a GIS (Grounding / RAG)
Místo spoléhání se na textový přepis od makléře bych do pipeline zapojila reálné datové zdroje:
* **ČÚZK API / RÚIAN:** Ověření skutečného typu vlastnictví, přesné výměry a zapsaných břemen přímo z listu vlastnictví.
* **LPIS API:** Ověření, zda je půda skutečně zařazena v půdních blocích, jaká je kultura a kdo pobírá dotace.
* **DIBAVOD / Ochrana přírody:** Automatické prostorové překrytí geometrie parcely s vrstvami aktivních záplavových zón (Q100) a chráněných území.

### 3. Pydantic validace a Structured Outputs
* V současném řešení spoléháme na JSON formátování v promptu a základní parsování. V produkci bych nasadila striktní **Pydantic model** s `Instructor` nebo nativní OpenAI/Gemini **Structured Outputs (JSON Schema)**, což zaručí neměnnost datových typů (např. že `skore_rizika` je vždy `int` v rozmezí 1–10).

### 4. Automatizovaný evaluační framework (CI/CD pro prompty)
* Vybudování datasetu 50+ reálných historických parcel Viagemu.
* Zavedení automatických testů, které při jakékoliv úpravě promptu spočítají metriky:
  * Shoda doporučení (`Accuracy / F1-score` pro `KOUPIT` / `PROVĚŘIT` / `ZAMÍTNOUT`).
  * Střední kvadratická chyba (`MSE`) u skóre rizika a likvidity.
  * Míra dodržení JSON schématu (Schema compliance rate).
