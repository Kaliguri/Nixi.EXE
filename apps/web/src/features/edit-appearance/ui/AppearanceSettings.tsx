import { useTranslation } from 'react-i18next';
import { cn } from '@/shared/lib/cn';
import { useTheme, THEMES, type ThemeId } from '@/shared/lib/useTheme';
import { useCrt } from '@/shared/lib/useCrt';
import { Toggle } from '@/shared/ui';

const themeLabelKey: Record<ThemeId, 'appearance.themeGreen' | 'appearance.themeAmber'> = {
  green: 'appearance.themeGreen',
  amber: 'appearance.themeAmber',
};

export function AppearanceSettings() {
  const { t } = useTranslation();
  const theme = useTheme((s) => s.theme);
  const setTheme = useTheme((s) => s.setTheme);
  const crt = useCrt((s) => s.on);
  const setCrt = useCrt((s) => s.set);

  return (
    <div className="max-w-md space-y-5">
      <div>
        <p className="mb-2 text-[11px] uppercase tracking-wide text-term-dim">
          {t('appearance.theme')}
        </p>
        <div className="grid grid-cols-2 gap-2">
          {THEMES.map((th) => {
            const active = theme === th.id;
            return (
              <button
                key={th.id}
                type="button"
                onClick={() => setTheme(th.id)}
                aria-pressed={active}
                className={cn(
                  'retro-press group flex items-center gap-2 border px-3 py-2 text-left transition-colors',
                  active
                    ? 'border-phosphor bg-phosphor/10'
                    : 'border-term-border bg-term-panel hover:border-term-dim',
                )}
              >
                {/* Свотч акцента темы + мини-«сканлайны». */}
                <span
                  className="h-6 w-6 shrink-0 border border-black/40"
                  style={{
                    backgroundColor: th.swatch,
                    boxShadow: active ? `0 0 8px ${th.swatch}` : 'none',
                    backgroundImage:
                      'repeating-linear-gradient(to bottom, rgba(0,0,0,0) 0 2px, rgba(0,0,0,0.25) 2px 3px)',
                  }}
                />
                <span
                  className={cn(
                    'text-xs',
                    active ? 'text-phosphor text-glow-soft' : 'text-term-fg',
                  )}
                >
                  {t(themeLabelKey[th.id])}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="space-y-1">
        <Toggle checked={crt} onChange={setCrt} label={t('appearance.crt')} />
        <p className="text-xs text-term-dim">{t('appearance.crtHint')}</p>
      </div>
    </div>
  );
}
