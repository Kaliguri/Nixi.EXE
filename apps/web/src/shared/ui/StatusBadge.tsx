import { useTranslation } from 'react-i18next';
import { cn } from '@/shared/lib/cn';
import type { EngineStateName } from '@/shared/api';

const meta: Record<EngineStateName, { dot: string; text: string }> = {
  stopped: { dot: 'bg-term-dim', text: 'text-term-dim' },
  loading: { dot: 'bg-amber animate-pulse', text: 'text-amber' },
  listening: { dot: 'bg-phosphor animate-pulse', text: 'text-phosphor' },
  recording: { dot: 'bg-phosphor animate-pulse', text: 'text-phosphor' },
  thinking: { dot: 'bg-coral animate-pulse', text: 'text-coral' },
  speaking: { dot: 'bg-cyan animate-pulse', text: 'text-cyan' },
  paused: { dot: 'bg-amber', text: 'text-amber' },
  error: { dot: 'bg-danger animate-pulse', text: 'text-danger' },
};

export function StatusBadge({ state }: { state: EngineStateName }) {
  const { t } = useTranslation();
  const m = meta[state];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 border border-term-border bg-term-panel px-2.5 py-1',
        'font-pixel text-[9px] uppercase leading-none text-glow-soft',
        m.text,
      )}
    >
      <span className={cn('h-2 w-2', m.dot)} />
      {t(`status.${state}`)}
    </span>
  );
}
