// Vendor pages messages

export const vendorMessages = {
  orders: {
    title: 'Zamówienia do realizacji',
    subtitle: 'Przeglądaj zamówienia przypisane do Twojej firmy',
    loading: 'Ładowanie zamówień...',
    error: 'Nie udało się załadować zamówień',
    retry: 'Spróbuj ponownie',
    emptyState: {
      title: 'Brak zamówień',
      description: 'Nie masz aktualnie żadnych przypisanych zamówień.',
    },
  },
  filters: {
    all: 'Wszystkie',
    planned: 'Zaplanowane',
    confirmed: 'Potwierdzone',
    delivered: 'Dostarczone',
    cancelled: 'Anulowane',
    dateFrom: 'Data od',
    dateTo: 'Data do',
    clearFilters: 'Wyczyść filtry',
  },
  table: {
    id: 'ID',
    office: 'Biurowiec',
    orderDate: 'Data zamówienia',
    deliveryDate: 'Data dostawy',
    quantity: 'Ilość',
    unitPrice: 'Cena jedn.',
    transportCost: 'Koszty transportu',
    totalCost: 'Koszt całkowity',
    status: 'Status',
    actions: 'Akcje',
    viewDetails: 'Szczegóły',
    changeStatus: 'Zmień status',
  },
  statusChange: {
    success: 'Status zamówienia został zmieniony',
    error: 'Nie udało się zmienić statusu zamówienia',
    updating: 'Aktualizuję...',
  },
  status: {
    planned: 'Zaplanowane',
    confirmed: 'Potwierdzone',
    delivered: 'Dostarczone',
    cancelled: 'Anulowane',
  },
};
