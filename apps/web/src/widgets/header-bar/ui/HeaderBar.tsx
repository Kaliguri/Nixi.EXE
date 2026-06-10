import { useTranslation } from 'react-i18next';
import { StatusBadge, CrtToggle } from '@/shared/ui';
import { LanguageSwitcher } from '@/shared/i18n';
import { cn } from '@/shared/lib/cn';
import { useSettings } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';
import { EngineControls } from '@/features/toggle-engine';

export function HeaderBar() {
  const { t } = useTranslation();
  const { data: settings } = useSettings();
  const state = useEngineStore((s) => s.state);
  const connected = useEngineStore((s) => s.connected);

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-term-border pb-4">
      <div className="flex items-center gap-3">
        <span
          className={cn(
            'h-2.5 w-2.5',
            connected
              ? 'animate-pulse bg-phosphor shadow-[0_0_6px_var(--color-phosphor)]'
              : 'bg-danger',
          )}
          title={connected ? t('header.online') : t('header.offline')}
        />
        <h1 className="glitch cursor-blink font-pixel text-sm uppercase text-phosphor text-glow">
          {settings?.assistant.name || t('header.assistant')}
        </h1>
        <StatusBadge state={state} />
      </div>
      <div className="flex items-center gap-2">
        <LanguageSwitcher />
        <CrtToggle />
        <EngineControls />
      </div>
    </header>
  );
}
