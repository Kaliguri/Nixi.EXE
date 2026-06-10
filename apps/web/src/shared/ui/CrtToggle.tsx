import { useTranslation } from 'react-i18next';
import { cn } from '@/shared/lib/cn';
import { useCrt } from '@/shared/lib/useCrt';

/** Кнопка-индикатор включения CRT-режима (сканлайны/свечение/фликер). */
export function CrtToggle() {
  const { t } = useTranslation();
  const on = useCrt((s) => s.on);
  const toggle = useCrt((s) => s.toggle);

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={on}
      title={t('ui.crtTitle')}
      className={cn(
        'retro-press inline-flex items-center gap-1.5 border px-2 py-1',
        'font-pixel text-[9px] uppercase leading-none transition-colors',
        on
          ? 'border-phosphor/60 bg-phosphor/15 text-phosphor text-glow'
          : 'border-term-border bg-term-panel text-term-dim hover:text-term-fg',
      )}
    >
      <span
        className={cn('inline-block h-2 w-2', on ? 'animate-pulse bg-phosphor' : 'bg-term-border')}
      />
      {t('ui.crt')}
    </button>
  );
}
