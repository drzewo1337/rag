### RAG system testing

This repo will contain a simple rag, that will support beekeeper decision making; 

# Lokalne LLM na MacBook Air M4 (24 GB RAM, 10-core GPU, 120 GB/s)

Podsumowanie wydajności i rekomendacji modeli uruchamianych lokalnie przez **Ollama**.

---

## 📊 Specyfikacja i Prędkość Generowania (Ollama)

| Klasa Modelu | Rekomendowane Modele | Kwantyzacja | Prędkość (tok/s) | Zużycie RAM | Charakterystyka pracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lekka (8B)** | `qwen3:8b`, `llama3.1:8b` | **Q8_0** lub **Q4_K_M** | **~18 – 24 tok/s** | ~6 - 9 GB | Błyskawiczna odpowiedź. Tekst pojawia się szybciej niż czytasz. Laptop pozostaje chłodny, idealne na baterii. |
| **Średnia (27B/32B)** | `qwen2.5:32b-instruct-q3_K_L` | **Q3_K_L** | **~7 – 10 tok/s** | ~13 - 15 GB | Tempo miarowego pisania. Wysoka inteligencja. Dłuższe generowanie może nagrzać laptopa (brak wentylatora). |
| **Ciężka (30B+ Coder)**| `qwen2.5-coder:32b-instruct-q3_K_L`| **Q3_K_L** | **~4 – 6 tok/s** | ~16 - 18 GB | Wolne działanie. Chwila namysłu przed odpowiedzią. Maksymalne obciążenie RAM i GPU. |

---

## 🎯 Kiedy stosować dany model?

*   **Qwen 3 (8B) / Llama 3.1 (8B)**
    *   *Zastosowanie:* Codzienna praca, szybkie pytania, burza mózgów, tłumaczenia, redagowanie tekstu.
    *   *Komenda Ollama:* `ollama run qwen3:8b` lub `ollama run llama3.1`
*   **Qwen 3.8 / 2.5 (27B/32B) w Q3**
    *   *Zastosowanie:* Trudne zadania logiczne, zaawansowane programowanie, analiza danych tekstowych wymagająca **100% prywatności**.
    *   *Komenda Ollama:* `ollama run qwen2.5:32b-instruct-q3_K_L`

---

## ⚔️ Lokalne Qwen vs GPT-5 (Stan na sierpień 2025)

*   **Pisanie kodu (Coding):** **Qwen 27B wygrywa lub remisuje**. W generowaniu pojedynczych funkcji i poprawności składni Open-Weights z serii Qwen dorównuje/prześciga bazowe GPT-5 z 2025 r.
*   **Logika i Matematyka:** **GPT-5 wygrywa**. Chmurowy gigant dzięki warstwom głębokiego myślenia (*Chain-of-Thought*) radzi sobie znacznie lepiej z wieloetapową nauką i wyższą matematyką. Qwen 27B w Q3 bywa podatny na zapętlenia logiczne.
*   **Ograniczenie sprzętowe (Kontekst):** Architektura zunifikowana 24 GB RAM w MacBooku Air ogranicza bezpieczny kontekst w Ollamie do **~8k - 16k tokenów**. Powyżej tej wartości plik wymiany (SWAP) drastycznie spowolni system. GPT-5 w chmurze obsługuje do 400k tokenów.

---

## 💡 Pro-tipy dla MacBooka Air M4

1.  **Framework MLX:** Jeśli chcesz zyskać **15-25% wyższą prędkość** (tok/s), zamiast Ollamy użyj programu **LM Studio** i pobieraj modele w natywnym dla Apple formacie **MLX**.
2.  **Thermal Throttling:** MacBook Air chłodzi się pasywnie. Przy długiej pracy z modelami 27B/32B górna obudowa zrobi się gorąca, a prędkość generowania może lekko spaść – to normalne zabezpieczenie procesora.
