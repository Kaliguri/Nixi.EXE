import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeId = 'green' | 'amber';

// Доступные цветовые темы (реколор токенов). swatch — цвет акцента для превью.
export const THEMES: { id: ThemeId; swatch: string }[] = [
  { id: 'green', swatch: '#4ee88f' },
  { id: 'amber', swatch: '#f0915e' },
];

type ThemeState = { theme: ThemeId; setTheme: (t: ThemeId) => void };

// Выбор темы персистится; атрибут data-theme на <html> вешается эффектом ниже.
export const useTheme = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'green',
      setTheme: (t) => set({ theme: t }),
    }),
    { name: 'ui-theme' },
  ),
);

/** Синхронизирует data-theme на <html> с состоянием стора. */
export function applyThemeAttr(theme: ThemeId) {
  document.documentElement.dataset.theme = theme;
}
