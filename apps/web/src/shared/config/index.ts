// Фронт и backend живут на одном origin (в деве — через Vite-прокси),
// поэтому базовый путь относительный.
export const API_BASE = '/api';

export function wsUrl(): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${proto}://${window.location.host}/ws`;
}
