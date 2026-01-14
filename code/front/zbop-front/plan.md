# Plan przepisania frontendu - Coffee Inventory Planning System

## Przegląd zmian

Aplikacja wymaga całkowitej przebudowy architektury w celu wprowadzenia:
- Systemu autentykacji z sesją w ciasteczku
- Widoków różniących się w zależności od roli użytkownika (user/vendor)
- Zarządzania zamówieniami (przeglądanie, tworzenie, edycja)

---

## Faza 1: Infrastruktura autentykacji

### 1.1 Serwis API (`src/services/api.ts`)
- [x] Utworzenie klienta HTTP (fetch/axios) z obsługą:
  - Base URL konfigurowalny (localhost:8000 / api:8000)
  - Automatyczne dodawanie tokenu JWT z ciasteczka do nagłówków
  - Interceptor do obsługi błędów 401 (przekierowanie na login)
  - Typowanie odpowiedzi zgodne z OpenAPI

### 1.2 Serwis autentykacji (`src/services/auth.ts`)
- [x] Implementacja funkcji:
  - `login(email, password)` → POST `/auth/login`
  - `register(userData)` → POST `/auth/register`
  - `getCurrentUser()` → GET `/auth/me`
  - `logout()` → usunięcie ciasteczka
- [x] Zarządzanie tokenem JWT w ciasteczku (HttpOnly jeśli możliwe, lub secure cookie)

### 1.3 Kontekst autentykacji (`src/context/AuthContext.tsx`)
- [x] React Context z:
  - Stan użytkownika (UserResponse | null)
  - Rola użytkownika (admin | manager | user | vendor)
  - Funkcje: login, logout, refreshUser
  - Flaga isLoading dla początkowego ładowania sesji
  - Flaga isAuthenticated

### 1.4 Hook `useAuth` (`src/hooks/useAuth.ts`)
- [x] Wygodny dostęp do kontekstu autentykacji
- [x] Pomocnicze funkcje sprawdzające uprawnienia

---

## Faza 2: Routing i ochrona tras

### 2.1 Komponent ProtectedRoute (`src/components/auth/ProtectedRoute.tsx`)
- [x] Wrapper chroniący trasy przed niezalogowanymi użytkownikami
- [x] Przekierowanie na `/login` gdy brak sesji
- [x] Opcjonalne sprawdzanie wymaganej roli

### 2.2 Aktualizacja routingu (`src/pages/App.tsx`)
- [x] Nowa struktura tras:
  ```
  /login          → Strona logowania (publiczna)
  /register       → Strona rejestracji (publiczna)
  /               → Przekierowanie na /orders/create (user) lub /vendor/orders (vendor)
  
  # Dla użytkownika (user/manager):
  /orders/create  → Tworzenie zamówienia (aktualny CreatePrediction)
  /orders         → Lista moich zamówień
  /orders/:id/edit → Edycja zamówienia
  
  # Dla vendora:
  /vendor/orders  → Lista zamówień powiązanych z vendorem
  ```

### 2.3 Layout z nawigacją (`src/components/layout/MainLayout.tsx`)
- [x] Navbar z zakładkami zależnymi od roli:
  - **User**: "Stwórz zamówienie" | "Moje zamówienia"
  - **Vendor**: "Zamówienia"
- [x] Wyświetlanie informacji o zalogowanym użytkowniku
- [x] Przycisk wylogowania

---

## Faza 3: Strony autentykacji

### 3.1 Strona logowania (`src/pages/auth/Login.tsx`)
- [x] Formularz z polami: email, password
- [x] Walidacja (Formik + Yup)
- [x] Obsługa błędów logowania (401)
- [x] Przekierowanie po zalogowaniu na odpowiednią stronę wg roli
- [x] Link do rejestracji

### 3.2 Strona rejestracji (`src/pages/auth/Register.tsx`)
- [x] Formularz z polami: email, password, first_name, last_name
- [x] Walidacja hasła (min 8 znaków)
- [x] Automatyczne logowanie po rejestracji lub przekierowanie na login
- [x] Link do logowania

### 3.3 Style dla stron auth (`src/pages/auth/styles.scss`)
- [x] Wyśrodkowany formularz
- [x] Responsywny design

---

## Faza 4: Serwisy zamówień

### 4.1 Serwis zamówień (`src/services/orders.ts`)
- [x] `getOrders(filters?)` → GET `/orders`
  - Filtry: office_id, status, date_from, date_to
- [x] `getOrder(id)` → GET `/orders/{id}`
- [x] `createOrder(data)` → POST `/orders`
- [x] `createCorrection(orderId, data)` → POST `/orders/{id}/corrections`
- [x] `getCorrections(orderId)` → GET `/orders/{id}/corrections`

### 4.2 Serwis optymalizacji (`src/services/optimization.ts`)
- [ ] `createOptimization(data)` → POST `/optimization/requests`
- [ ] `getOptimization(id)` → GET `/optimization/requests/{id}`

### 4.3 Typy TypeScript (`src/types/`)
- [x] `src/types/auth.ts` - UserResponse, TokenResponse, UserLogin, UserRegister
- [x] `src/types/orders.ts` - OrderResponse, OrderCreate, OrderCorrectionCreate, OrderCorrectionResponse
- [x] `src/types/optimization.ts` - OptimizationRequestCreate, OptimizationRequestResponse
- [x] `src/types/common.ts` - ErrorResponse, ValidationError

---

## Faza 5: Widok użytkownika - Lista zamówień

### 5.1 Strona listy zamówień (`src/pages/orders/OrdersList.tsx`)
- [x] Pobieranie zamówień użytkownika (filtrowane po office_id użytkownika)
- [x] Kafelki (cards) dla każdego zamówienia zawierające:
  - Data zamówienia
  - Status (planned/confirmed/delivered/cancelled)
  - Ilość (kg)
  - Koszt całkowity
  - Przycisk "Popraw zamówienie" → `/orders/:id/edit`
- [x] Stany ładowania i błędów
- [x] Pusta lista - komunikat zachęcający do stworzenia zamówienia

### 5.2 Komponent kafelka zamówienia (`src/components/orders/OrderCard.tsx`)
- [x] Wyświetlanie szczegółów zamówienia (zintegrowane w OrdersList)
- [x] Kolorystyka statusu (badge)
- [x] Przycisk akcji edycji

### 5.3 Style (`src/pages/orders/styles.scss`)
- [x] Grid kafelków responsywny
- [x] Style kart
- [x] Style statusów

---

## Faza 6: Edycja zamówienia (korekta)

### 6.1 Strona edycji (`src/pages/orders/EditOrder.tsx`)
- [x] Pobieranie szczegółów zamówienia po ID z URL
- [x] Formularz korekty:
  - Zwiększenie ilości (quantity_increase)
  - Zmniejszenie ilości (quantity_decrease)
  - Powód korekty (reason)
- [x] Wyświetlenie aktualnych danych zamówienia (readonly)
- [x] Historia poprzednich korekt
- [x] Przycisk powrotu do listy

### 6.2 Komponent formularza korekty (`src/components/orders/CorrectionForm.tsx`)
- [x] Walidacja (zintegrowane w EditOrder)
- [x] Podgląd nowej ilości po korekcie

---

## Faza 7: Widok vendora

### 7.1 Strona zamówień vendora (`src/pages/vendor/VendorOrders.tsx`)
- [x] Pobieranie zamówień gdzie distributor_id = ID vendora
- [x] Tabela/lista zamówień z:
  - Biurowiec (office)
  - Data zamówienia i dostawy
  - Ilość
  - Status
  - Koszt
- [x] Filtry: status, zakres dat
- [ ] Możliwość zmiany statusu (jeśli vendor ma uprawnienia)

### 7.2 Style (`src/pages/vendor/styles.scss`)
- [x] Style tabeli/listy
- [x] Style filtrów

---

## Faza 8: Aktualizacja istniejących komponentów

### 8.1 Modyfikacja CreatePrediction (`src/pages/create-prediction/CreatePrediction.tsx`)
- [x] Zmiana nazwy na "Stwórz zamówienie" (lub pozostawienie jako Create Order)
- [x] Po utworzeniu zamówienia:
  - Przekierowanie na listę zamówień
  - Lub wyświetlenie potwierdzenia z linkiem do listy
- [ ] Dodanie office_id z kontekstu użytkownika

### 8.2 Aktualizacja Form (`src/components/form/Form.tsx`)
- [ ] Dodanie brakujących pól zgodnych z OptimizationRequestCreate:
  - purchase_costs_daily
  - transport_cost
- [ ] Usunięcie/ukrycie pól które są pobierane z profilu (office_id)

### 8.3 Aktualizacja messages.ts
- [x] Polskie tłumaczenia (jeśli wymagane)
- [x] Nowe komunikaty dla nowych funkcjonalności

---

## Faza 9: Konfiguracja i utilities

### 9.1 Konfiguracja API (`src/config/api.ts`)
- [x] Base URL z environment variables
- [x] Timeout settings
- [ ] Retry logic

### 9.2 Utilities (`src/utils/`)
- [x] `cookies.ts` - funkcje do zarządzania ciasteczkami
- [ ] `formatters.ts` - formatowanie dat, kwot, ilości
- [ ] `validators.ts` - wspólne walidatory

---

## Faza 10: Testy

### 10.1 Testy jednostkowe
- [ ] Testy serwisów (mocki API)
- [ ] Testy hooków
- [ ] Testy komponentów

### 10.2 Testy integracyjne
- [ ] Flow logowania
- [ ] Flow tworzenia zamówienia
- [ ] Flow korekty zamówienia

---

## Struktura katalogów po zmianach

```
src/
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx
│   ├── form/
│   │   ├── Form.tsx (zaktualizowany)
│   │   ├── messages.ts
│   │   └── styles.scss
│   ├── layout/
│   │   ├── MainLayout.tsx
│   │   ├── Navbar.tsx
│   │   └── styles.scss
│   ├── orders/
│   │   ├── OrderCard.tsx
│   │   ├── CorrectionForm.tsx
│   │   └── styles.scss
│   └── predictionResults/
│       └── (bez zmian)
├── context/
│   └── AuthContext.tsx
├── hooks/
│   ├── useAuth.ts
│   └── useOrders.ts
├── pages/
│   ├── App.tsx (zaktualizowany routing)
│   ├── auth/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── styles.scss
│   ├── create-prediction/
│   │   └── (zaktualizowany)
│   ├── orders/
│   │   ├── OrdersList.tsx
│   │   ├── EditOrder.tsx
│   │   └── styles.scss
│   └── vendor/
│       ├── VendorOrders.tsx
│       └── styles.scss
├── services/
│   ├── api.ts
│   ├── auth.ts
│   ├── orders.ts
│   └── optimization.ts
├── types/
│   ├── auth.ts
│   ├── orders.ts
│   ├── optimization.ts
│   └── common.ts
├── utils/
│   ├── cookies.ts
│   └── formatters.ts
└── config/
    └── api.ts
```

---

## Zależności do dodania

```json
{
  "dependencies": {
    "js-cookie": "^3.0.5",
    "@types/js-cookie": "^3.0.6"
  }
}
```

Opcjonalnie:
- `axios` - jeśli preferowany nad fetch
- `react-query` / `@tanstack/react-query` - dla cachowania i zarządzania stanem serwerowym

---

## Kolejność implementacji

1. **Typy TypeScript** (types/) - podstawa dla całej aplikacji
2. **Konfiguracja API** (config/, services/api.ts)
3. **Serwis autentykacji** (services/auth.ts)
4. **Kontekst i hook autentykacji** (context/, hooks/)
5. **Strony logowania/rejestracji** (pages/auth/)
6. **Layout i nawigacja** (components/layout/)
7. **ProtectedRoute i aktualizacja routingu** (App.tsx)
8. **Serwis zamówień** (services/orders.ts)
9. **Lista zamówień użytkownika** (pages/orders/)
10. **Edycja zamówienia** (pages/orders/EditOrder.tsx)
11. **Widok vendora** (pages/vendor/)
12. **Aktualizacja CreatePrediction**
13. **Testy**

---

## API Endpoints wykorzystywane

| Funkcjonalność | Metoda | Endpoint |
|----------------|--------|----------|
| Logowanie | POST | `/auth/login` |
| Rejestracja | POST | `/auth/register` |
| Dane użytkownika | GET | `/auth/me` |
| Lista zamówień | GET | `/orders` |
| Szczegóły zamówienia | GET | `/orders/{id}` |
| Nowe zamówienie | POST | `/orders` |
| Korekta zamówienia | POST | `/orders/{id}/corrections` |
| Historia korekt | GET | `/orders/{id}/corrections` |
| Optymalizacja | POST | `/optimization/requests` |

---

## Uwagi

1. **Rozróżnienie user/vendor**: W API nie ma bezpośredniej roli "vendor", ale jest `distributor_id`. Zakładam, że vendor to użytkownik powiązany jako dystrybutor. Może być potrzebne dodatkowe pole w `UserResponse` lub logika oparta na `distributor_id`.

2. **Sesja w ciasteczku**: Token JWT będzie przechowywany w ciasteczku. Dla bezpieczeństwa zalecane `HttpOnly` i `Secure`, ale wymaga to obsługi po stronie serwera. Na froncie używamy `js-cookie` dla non-HttpOnly cookies.

3. **Legacy endpoint**: `/create_predictions_v2` jest zachowany dla kompatybilności, ale nowa implementacja powinna używać `/optimization/requests`.

4. **Filtrowanie zamówień vendora**: Potrzebne będzie API do pobierania zamówień gdzie `distributor_id` odpowiada ID vendora, lub endpoint dedykowany dla vendorów.
