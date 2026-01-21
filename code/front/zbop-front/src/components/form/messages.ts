export const messages = {
  title: 'Planowanie zamówień kawy',
  fields: {
    planningHorizonDays: 'Horyzont planowania (dni)',
    numConferencesDaily: 'Liczba konferencji dziennie',
    numWorkersDaily: 'Liczba pracowników dziennie',
    fillAllConferences: 'Wypełnij wszystkie dni tą samą wartością',
    fillAllWorkers: 'Wypełnij wszystkie dni tą samą wartością',
    storageCapacityKg: 'Pojemność magazynu (kg)',
    initialInventoryKg: 'Początkowy stan magazynu (kg)',
    officeLocation: 'Lokalizacja biura',
    advancedSettingsExpanded: 'Edytuj stałe (kliknij aby zwinąć)',
    advancedSettingsCollapsed: 'Edytuj stałe (kliknij aby rozwinąć)',
  },
  actions: {
    submit: 'Stwórz plan zamówienia',
    reset: 'Resetuj',
  },
  validation: {
    required: 'To pole jest wymagane',
    number: 'Wprowadź poprawną liczbę',
    integer: 'Wprowadź liczbę całkowitą',
    nonNegative: 'Wartość musi być nieujemna',
    positive: 'Wartość musi być dodatnia',
    between0and1: 'Wartość musi być między 0.0 a 1.0',
    positiveFloat: 'Wprowadź dodatnią liczbę dziesiętną',
  },
  predictionResult: {
    title: 'Prognoza zamówień i zużycia kawy',
    headers: {
      day: 'Dzień',
      orderAmount: 'Ilość zamówienia',
      consumedAmount: 'Zużycie',
      remainingAmount: 'Pozostało',
      unit: 'Jednostka',
    },
    noResults: 'Brak wyników prognozy. Wypełnij formularz powyżej, aby wygenerować prognozę.',
  },
  createPrediction: {
    title: 'System planowania kawy',
    subtitle: 'Wprowadź parametry poniżej, aby optymalnie zaplanować zamówienia kawy dla Twojego biura.',
    successMessage: 'Plan zamówienia został pomyślnie utworzony!',
    errorMessage: 'Wystąpił błąd podczas tworzenia planu zamówienia.',
    goToOrders: 'Przejdź do zamówień',
  },
};


