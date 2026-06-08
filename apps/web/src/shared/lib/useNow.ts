import { useEffect, useState } from 'react';

/** Тикающее «сейчас» для затухания VU-метров между событиями. */
export function useNow(intervalMs = 120): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), intervalMs);
    return () => window.clearInterval(id);
  }, [intervalMs]);
  return now;
}
