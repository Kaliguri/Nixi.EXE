import { cn } from '@/shared/lib/cn';
import type { EngineStateName } from '@/shared/api';

const meta: Record<EngineStateName, { label: string; dot: string; text: string }> = {
  stopped: { label: 'Остановлен', dot: 'bg-zinc-500', text: 'text-zinc-400' },
  loading: { label: 'Загрузка…', dot: 'bg-amber-400 animate-pulse', text: 'text-amber-300' },
  listening: { label: 'Слушаю', dot: 'bg-emerald-400 animate-pulse', text: 'text-emerald-300' },
  recording: { label: 'Запись', dot: 'bg-emerald-400 animate-pulse', text: 'text-emerald-300' },
  thinking: { label: 'Думаю', dot: 'bg-indigo-400 animate-pulse', text: 'text-indigo-300' },
  speaking: { label: 'Говорю', dot: 'bg-sky-400 animate-pulse', text: 'text-sky-300' },
  paused: { label: 'Пауза', dot: 'bg-amber-400', text: 'text-amber-300' },
  error: { label: 'Ошибка', dot: 'bg-rose-500', text: 'text-rose-400' },
};

export function StatusBadge({ state }: { state: EngineStateName }) {
  const m = meta[state];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1 text-sm font-medium',
        m.text,
      )}
    >
      <span className={cn('h-2 w-2 rounded-full', m.dot)} />
      {m.label}
    </span>
  );
}
