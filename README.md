### Zadanie rekrutacyjne 
---
Celem tego zadania było stworzenie taksonomii marek różnych rodzajów alkoholi, które można rozpoznać w naszych danych. Aby tego dokonać, musieliśmy zacząć od przygotowania listy alkoholi. Następnym krokiem było przygotowanie odpowiednich zapytań i przetestowanie ich w estymatorze. W efekcie mieliśmy otrzymać możliwie najdłuższą listę odnalezionych marek alkoholi wraz z definicjami zapytań, które były w stanie przypisać adresy URL do danej pozycji. Na liście powinny pojawić się tylko pozycje, które złapały przynajmniej jeden dobry adres URL. Zwrócony wynik miał mieć postać pliku JSON o nazwie inazwisko.json (na przykład dla Jana Kowalskiego jkowalski.json) z listą zapytań, w których zostało dodane dodatkowe pole "id" z nazwą danego alkoholu.

Opis plików
- `alcohols.json` - plik zawierający uporządkowane marki alkoholi wraz z opcjonalnymi słowami kluczowymi dla każdej kategorii.
- `alcohols.xlsx` - plik zawierający dane na temat marek alkoholi oraz ich typów.
- `create_alcohol_list.py` - skrypt, który na podstawie informacji zawartych w pliku alcohols.xlsx oraz słów kluczowych (zawartych w pliku keywords.json) tworzy plik alcohols.json.
- `keywords.json` - plik zawierający informacje na temat opcjonalnych słów kluczowych dla każdej kategorii.
- `main.py` - główny skrypt, który na podstawie informacji zawartych w pliku alcohols.json testuje poszczególne zapytania i zwraca trafne wyniki do pliku o nazwie mmachnowski.json.
- `mmachnowski.json` - plik wynikowy zawierający końcową listę zapytań wraz z przypisanymi identyfikatorami dla poszczególnych marek alkoholi.
---
Podczas tworzenia taksonomii marek różnych alkoholi zdecydowałem się na podział na dwie główne kategorie: destylowane i fermentowane. W kategorii destylowane umieściłem siedem podstawowych rodzajów alkoholi: vodka, whisky, gin, rum, tequila, brandy oraz mezcal. Natomiast w kategorii fermentowane znalazły się beer, wine, cider oraz sake.

Rozpocząłem zadanie od przygotowania listy marek alkoholi. Skorzystałem z gotowych danych i połączyłem je w jeden wspólny plik. Dla każdej kategorii i rodzaju alkoholu przygotowałem także listę opcjonalnych słów kluczowych, które najczęściej występują z danym alkoholem. Znajdują się one w pliku keywords.json. Ich celem jest dodanie do zapytania słów opcjonalnych, które pomogą zawęzić zapytanie i znaleźć dokładnie to, o co pytamy.

Następnym krokiem było stworzenie skryptu, który połączył ze sobą informacje na temat marek alkoholi i słów opcjonalnych dla każdej kategorii i rodzaju. Skrypt ten przechodzi przez listę marek alkoholi i umieszcza każdy z nich w odpowiednim miejscu. To samo robi dla słów opcjonalnych.

W mojej strategii zastosowałem podejście konstruktywne. Wychodziłem od jak najogólniejszego zapytania i sukcesywnie je zawężałem poprzez zmianę trybu, dodawanie słów opcjonalnych i zwiększanie opcjonalnego progu trafności (optionalThreshold). W przypadku braku wyników dla danego zapytania, skrypt przechodził do kolejnego, bardziej szczegółowego zapytania. Jeśli estymator znalazł jakiś adres URL dla marki alkoholu z trybem C, to wysyłał kolejne zapytanie tym razem z trybem M. Jeśli znowu otrzymywał wynik, to dodawał opcjonalne słowa kluczowe do zapytania i ustawiał opcjonalny próg trafności na 1. Jeśli zapytanie zwracało wynik, to zwiększał opcjonalny próg trafności o jeden w celu zwiększenia pewności, że znaleziony przez nas adres URL na pewno dotyczy tego, czego szukamy. W przypadku, gdy zwiększenie opcjonalnego progu trafności nie dawało rezultatów, to skrypt wracał do poprzedniego zapytania, usuwał od końca słowa opcjonalne i ponownie je wykonywał. W przypadku, gdy usunięcie słowa opcjonalnego nie dawało żadnych wyników, to skrypt wracał do ostatniego zapytania, które zwróciło wynik i zapisywał je w końcowym pliku.

Ze względu na interpretację zadania, chciałem, aby zwracane adresy URL dotyczyły dokładnie tego alkoholu, który nas interesuje. Dlatego też zdecydowałem się nie dodawać do końcowej listy alkoholi, które zwróciły wynik dla ogólnych zapytań bez słów opcjonalnych.
