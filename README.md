# log-parser

### uruchomienie
python parse.py --from 20-11-2020_10-20-30 --to 21-12-2020_10-20-30 gunicorn.log2

uruchomienie z flagą -h podaje szczegóły opcji <br/>
python parse.py -h

### zamysł rozwiązania
1) podany format logów jest konwertowany na wyrazenie regularne
2) obliczane są poprawne daty startu i zakończenia
3) Przechodząc po linijkach pliku:<br/>
    matchujemy linijke do wzorca<br/>
    sprawdzamy czy data jest w interesującym nas zakresie<br/>
    aktualizujemy statystyki przkazując obiekt matchu do metody "update_stat"<br/>

Statystyki tworzone są w formie klas dziedziczących po abstrakcyjnej klasie Statistic (w pliku statistics_classes.py),
kazda statystyka ma swoje wymagane pola (pola z logów z których będzie korzystać, jeśli ich nie ma pojawia się stosowny komunikat, a statystyka nie jest liczona), dodatkowo posiada metodę \_\_repr\_\_, give_answer oraz update_stat <br/>
update_stat przyjmuje obiekt matchu i na jego podstawie aktualizuje dane <br/>
give_answer zwraca odpowiedź danej statystyki <br/>
\_\_repr\_\_ wyświetla odpowiedź w odpowiedni sposób </br>

### modyfikacje i analiza
Przyjęte podejście pozwala bardzo łatwo modyfikować program:<br/>
Lista statystyk obliczanych w trakcie działania znajduje się w pliku config.py, aby dodać nową statystykę wystarczy stworzyć dla niej klasę i dodać ją do listy <br/>
Podobnie format logów znajduje się w pliku config.py i mozna go łatwo zmienić w razie potrzeby, bo wyrazenie mu odpowiadajace się dostosuje <br/>
Aby zmienic kolejność czy sposób wyświetlania statystyk wystarczy zmienić ich kolejność na liście oraz zmodyfikować metody \_\_repr\_\_ <br/>

Program nie wczytuje całego pliku do pamięci.<br/>
Program działa dosyć wolno - co ciekawe, jak pokazuje profiler, nie jest to spowodowane skomplikowanymi wyrazeniami regularnymi, a korzystaniem z funkcji strptime przy parsowaniu daty, która okazuje się być bardzo wolna. Mozna rozwiązać ten problem pisząc swoją funkcję lub/i korzystając z wyrazeń regularnych. Szybkie sprawdzenie w googlu mówi, ze moze to dać około 4-krotne przyspieszenie, ale nie miałem juz czasu tego zaimplementowac.<br/>
Inną potencjalną optymalizacją czasową, która niestety wymaga juz wczytania pliku do pamięci jest zastosowanie binsearcha do znalezienia odpowiedniego fragmentu. Zrezygnowałem z takiego rozwiązania poniewaz złozoność pamięciowa jest wyzej na liście priorytetów.


### testy
testy mozna uruchomić przy pomocy
pytest tests.py

są one podzielona na trzy grupy re/date/stat, które mozna uruchomic niezaleznie
sprawdzam w szczególności czy tworzy się poprawny wzorzec, czy wyrazenie dobrze parsuje logi, czy obliczana jest poprawna data oraz czy w końcu wyniki programu są takie jak byśmy chcieli.


![](https://i.imgur.com/eQ7zKZg.jpg)


