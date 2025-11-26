import { FormValues } from './Form';

export async function submitFormData(payload: FormValues): Promise<void> {
  // TODO: Replace with real API call when backend is available
  // Example:
  // await fetch('/api/parameters', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(payload),
  // });
  // Temporary no-op to simulate async call
  return new Promise((resolve) => {
    // eslint-disable-next-line no-console
    console.log('Submitting form payload', payload);
    setTimeout(resolve, 300);
  });
}


