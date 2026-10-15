# AI / ML Notes

Blog: https://grjus.github.io/

Prosta strona Jekyll publikowana przez GitHub Pages z katalogu głównego gałęzi `main`.

## Dodawanie wpisów

Utwórz `_posts/YYYY-MM-DD-krotki-tytul.md` z metadanymi:

```yaml
---
title: "Tytuł wpisu"
date: 2026-10-15 12:00:00 +0200
description: "Krótki opis na stronie głównej."
category: Badania i narzędzia
---
```

Po metadanych dodaj treść w Markdown. Podawaj linki do przeczytanych źródeł przy twierdzeniach, odróżniaj fakty od własnej oceny i sprawdzaj wcześniejsze wpisy, żeby nie powtarzać tematu. Data wpisu musi odpowiadać dniu publikacji i nie może być przyszła.

Zapis przez integrację GitHub ma tworzyć commit na `main`. GitHub Pages buduje Jekylla automatycznie. Nie dodajemy `.nojekyll`. Wynik publikacji sprawdzaj w Actions i na publicznym adresie wpisu.

## Zakres pierwszego testu

Pierwszy test integracji GitHub w interaktywnej sesji Codexa zakończył się błędem `403 Resource not accessible by integration` przy próbach zapisu przez Contents API i Git Trees API. Odczyt repozytorium działa, ale uprawnienia konta nie oznaczają uprawnień zapisu aplikacji.

Publikacja przez lokalne `gh` służy do osobnego sprawdzenia strony i GitHub Pages. Nie potwierdza działania zapisu w chmurze. Po nadaniu integracji uprawnień zapisu trzeba powtórzyć test, a następnie uruchomić zadanie na webie i sprawdzić wykonanie bez interaktywnego zatwierdzania. Harmonogram dzienny nie jest jeszcze skonfigurowany.
