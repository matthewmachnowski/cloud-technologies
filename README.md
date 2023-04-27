### Zadanie rekrutacyjne 
---
Celem tego zadania było stworzenie taksonomii marek różnych rodzajów alkoholi, które można rozpoznać w naszych danych. Aby tego dokonać, musieliśmy zacząć od przygotowania listy alkoholi. Następnym krokiem było przygotowanie odpowiednich zapytań i przetestowanie ich w estymatorze. W efekcie mieliśmy otrzymać możliwie najdłuższą listę odnalezionych marek alkoholi wraz z definicjami zapytań, które były w stanie przypisać adresy URL do danej pozycji. Na liście powinny pojawić się tylko pozycje, które złapały przynajmniej jeden dobry adres URL. Zwrócony wynik miał mieć postać pliku JSON o nazwie inazwisko.json (na przykład dla Jana Kowalskiego jkowalski.json) z listą zapytań, w których zostało dodane dodatkowe pole "id" z nazwą danego alkoholu.

Opis plików
- `alcohols.json` - plik zawierający uporządkowane marki alkoholi wraz z opcjonalnymi słowami kluczowymi dla każdej kategorii.
- `alcohols.xlsx` - plik zawierający dane na temat marek alkoholi oraz ich typów.
- `create_alcohol_list.json` - skrypt, który na podstawie informacji zawartych w pliku alcohols.xlsx oraz słów kluczowych (zawartych w pliku keywords.json) tworzy plik alcohols.json.
- `keywords.json` - plik zawierający informacje na temat opcjonalnych słów kluczowych dla każdej kategorii.
- `main.py` - główny skrypt, który na podstawie informacji zawartych w pliku alcohols.json testuje poszczególne zapytania i zwraca trafne wyniki do pliku o nazwie mmachnowski.json.
- `mmachnowski.json` - plik wynikowy zawierający końcową listę zapytań wraz z przypisanymi identyfikatorami dla poszczególnych marek alkoholi.
---
