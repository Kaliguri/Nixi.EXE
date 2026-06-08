/** Склейка классов с отбрасыванием falsy-значений. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ');
}
