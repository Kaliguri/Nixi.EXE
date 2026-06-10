import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGS } from './config';
import { cn } from '@/shared/lib/cn';

/** Ретро-сегментед-переключатель языка: [ RU | EN ]. */
export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const current = (i18n.resolvedLanguage ?? i18n.language ?? 'ru').slice(0, 2);

  return (
    <div
      className="inline-flex items-center border border-term-border bg-term-panel"
      role="group"
      aria-label={t('ui.language')}
    >
      {SUPPORTED_LANGS.map((lng) => {
        const active = current === lng;
        return (
          <button
            key={lng}
            type="button"
            onClick={() => void i18n.changeLanguage(lng)}
            aria-pressed={active}
            className={cn(
              'px-2 py-1 font-pixel text-[9px] uppercase leading-none transition-colors',
              active
                ? 'bg-phosphor/15 text-phosphor text-glow'
                : 'text-term-dim hover:text-term-fg',
            )}
          >
            {lng}
          </button>
        );
      })}
    </div>
  );
}
