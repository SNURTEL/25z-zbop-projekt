---
title: System wspomagający zamawianie kawy do budynków biurowych
subtitle: ZBOP Prezentacja Organizacyjna
author:
- Krzysztof Fijałkowski
- Jakub Kordel
- Tomasz Owienko
- Tomasz Świderski
date: 27.10.2025
documentclass: article
geometry:
- margin=1in
fontenc: T1
fontfamily: mlmodern
fontsize: 11pt
numbersections: true
---

# Kontekst i motywacja problemu

Celem projektu jest opracowanie systemu wspomagającego planowanie zamówień kawy do budynków biurowych w sposób minimalizujący koszty i straty. Model ma uwzględniać zmienność dziennego zapotrzebowania wynikającą z liczby pracowników, konferencji oraz pogody, a także ograniczenia dotyczące świeżości kawy i kosztów jej zakupu. Drugi model optymalizuje dostawy z centralnego magazynu, w którym kawa może być przechowywana dłużej. Kontekstem jest zminimalizowanie szansy braku kawy w biurze przy jednoczesnym nie przekroczeniu pojemności biura na kawę oraz minimalny sumaryczny koszt zakupu kawy.

# Interakcja użytkownika

Z perspektywy użytkownika system umożliwia wprowadzanie danych dotyczących liczby pracowników, planowanych konferencji. Użytkownik może przeglądać dzienne podsumowania zużycia kawy oraz rekomendacje dotyczące optymalnych zamówień na najbliższe dni. Wszystkie dane i prognozy są dostępne po zalogowaniu na indywidualne konto, co pozwala śledzić historię i koszty zamówień.

# Wstępny model do zamawiania kawy z perspektywy biurowca

## Założenia

Model zakłada, że każde biuro musi być codziennie zaopatrzone w odpowiednią ilość świeżej kawy, przy jednoczesnej minimalizacji nadwyżek i kosztów. Zapotrzebowanie na kawę zależy od liczby obecnych pracowników, liczby konferencji oraz pogody. Ceny kawy zmieniają się codziennie, a jej świeżość jest ograniczona do trzech dni. Zadaniem jest jednoczesne zminimalizowanie szansy braku kawy w biurze oraz kosztów dostaw i magazynowania.

## Zbiory

- Zbiór dni

## Parametry

Parametrami modelu są dzienne ceny kawy, prognozowana liczba pracowników i konferencji, współczynnik wpływu pogody na konsumpcję. Dodatkowo uwzględnia się dostępność kawy w magazynie centralnym i czas potrzebny na dostawę. Wszystkie dane są aktualizowane cyklicznie na podstawie informacji wprowadzanych przez użytkownika. 

## Zmienne decyzyjne

- Ilość sprowadzanej kawy z centralnego magazynu

## Ograniczenia

Kawa nie może być przechowywana dłużej niż trzy dni w biurze. Łączna ilość zamówionej kawy nie może przekroczyć pojemności biura na kawę. Koszt całkowity powinien być minimalny przy zapewnieniu ciągłości dostaw do wszystkich biur.

# Wstępny model dostarczania kawy do biurowców

## Założenia

Zakładamy, że koszt dostarczenia kawy z centralnego magazynu zależy od biurowca i od dnia. Chcemy zminimalizować koszty magazynowania i transportu maksymalizując zysk ze sprzedaży biurowcom. Czas transportu do magazynu od producenta zajmuje 2 tygodnie. Transport z magazynu do biura odbywa się następnego dnia.

## Zbiory

- Zbiór biurowców
- Zbiór dni

## Parametry

- Dzienne zapotrzebowanie na kawę w biurowcach
- Koszty dostarczenia kawy do biurowców
- Cena kawy u producenta jest zmienna

## Zmienne decyzyjne

- Ile zamiawia kawy od producenta

## Ograniczenia

- Pojemność magazynu


# Technologie

Jako technologie zostaną wykorzystane:

- Python (Fastapi)
- Solver: cplex
- GUI: TS (React)
- docker compose
- sqlite

# Organizacja pracy grupowej

Komunikacja przez Discord, kod źródłowy projektu w repozytorium [GitHub](https://github.com/SNURTEL/25z-zbop-projekt) 
