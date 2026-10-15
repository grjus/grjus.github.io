---
title: "Google Deep Review: AI sprawdza dokumenty techniczne"
date: 2026-10-15 12:00:00 +0200
description: "Nowe narzędzie Google wyrasta z pilota dla autorów prac naukowych. Sprawdzamy, co pokazują wyniki i czego z nich nie wynika."
category: Badania i narzędzia
---

14 października Google [ogłosiło publiczne udostępnienie Deep Review](https://research.google/blog/analyzing-technical-documents-with-deep-review/). System ma sprawdzać rozumowanie i twierdzenia w dokumentach technicznych. Wywodzi się z Paper Assistant Tool (PAT), używanego przez autorów prac przed zgłoszeniem na konferencję.

## Jak działa

Według opisu Google proces obejmuje cztery etapy: podział dokumentu na fragmenty, przydzielenie im budżetu obliczeń, równoległą weryfikację i złożenie wyników w raport. Agenci analizują przypisane fragmenty, zachowując dostęp do kontekstu całego dokumentu. Końcowy etap obejmuje też sprawdzanie informacji w źródłach zewnętrznych. [Opis architektury](https://research.google/blog/analyzing-technical-documents-with-deep-review/).

## Co pokazuje badanie PAT

W [preprincie z 26 czerwca](https://arxiv.org/html/2606.28277v1) autorzy porównali PAT z pojedynczym wywołaniem Gemini 3.1 Pro. Użyli wybranego podzbioru SPOT: 26 prac z matematyki i informatyki, zawierających 29 znanych błędów w równaniach lub dowodach.

| Metoda | Wykrywalność błędów w tym podzbiorze |
| --- | --- |
| Gemini 3.1 Pro, pojedyncze wywołanie | 55,2% |
| PAT z Gemini 3.1 Pro | 89,7% |

Różnica wynosi **34,5 punktu procentowego**. To wynik na małej, wyselekcjonowanej próbie. Nie opisuje skuteczności sprawdzania dowolnego dokumentu ani aktualnej wersji Deep Review. Autorzy zastosowali własny sposób oceniania odpowiedzi, więc przestrzegają przed bezpośrednim porównywaniem liczb z oryginalnym badaniem SPOT. Oceny automatyczne kontrolował człowiek. [Metodologia i wyniki](https://arxiv.org/html/2606.28277v1#S2.SS1).

## Co mówią autorzy prac

[Podsumowanie pilota ICML](https://blog.icml.cc/2026/03/30/retrospective-on-pat-x-icml-2026-ai-paper-assistant-program/) opisuje około 4500 przeanalizowanych prac i 869 odpowiedzi w ankiecie. Chęć ponownego użycia narzędzia zadeklarowało 92,1% respondentów. Wśród autorów prac z wynikami eksperymentalnymi 31% zgłosiło, że uwagi skłoniły ich do nowych eksperymentów.

To deklaracje uczestników, bez grupy kontrolnej. Raporty PAT otrzymywali wyłącznie autorzy; nie były częścią formalnej recenzji konferencyjnej. [Zasady i wyniki pilota](https://blog.icml.cc/2026/03/30/retrospective-on-pat-x-icml-2026-ai-paper-assistant-program/).

## Nasza ocena

Najciekawszy jest pomysł przeznaczania osobnego etapu pracy na szukanie błędów. Przy automatycznym pisaniu bloga warto zastosować podobną zasadę: najpierw zebrać materiały i napisać szkic, potem sprawdzić liczby, daty i zgodność twierdzeń ze źródłami.

Przedstawione wyniki uzasadniają zainteresowanie narzędziem, ale nie dają podstaw do traktowania jego raportu jako certyfikatu poprawności. Ten wpis jest analizą źródeł; nie przeprowadziliśmy własnego testu Deep Review.
