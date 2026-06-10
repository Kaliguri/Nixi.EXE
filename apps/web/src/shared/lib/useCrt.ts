import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type CrtState = { on: boolean; toggle: () => void; set: (v: boolean) => void };

// Тумблер «CRT mode»: усиленные сканлайны / вигнетка / фликер / свечение.
// Выбор персистится; класс `crt` вешается на <html> эффектом ниже.
export const useCrt = create<CrtState>()(
  persist(
    (set) => ({
      on: false,
      toggle: () => set((s) => ({ on: !s.on })),
      set: (v) => set({ on: v }),
    }),
    { name: 'crt-mode' },
  ),
);

/** Синхронизирует класс `crt` на <html> с состоянием стора. */
export function applyCrtClass(on: boolean) {
  document.documentElement.classList.toggle('crt', on);
}
