import { useEffect, useMemo, useRef } from 'react';

/** Возвращает дебаунс-обёртку колбэка (например, чтобы не писать config.yaml на каждый тик слайдера). */
export function useDebouncedCallback<A extends unknown[]>(
  fn: (...args: A) => void,
  delay = 300,
): (...args: A) => void {
  const fnRef = useRef(fn);
  fnRef.current = fn;
  const timer = useRef<number>();

  useEffect(() => () => window.clearTimeout(timer.current), []);

  return useMemo(
    () =>
      (...args: A) => {
        window.clearTimeout(timer.current);
        timer.current = window.setTimeout(() => fnRef.current(...args), delay);
      },
    [delay],
  );
}
