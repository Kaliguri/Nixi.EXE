import { StatusBadge } from '@/shared/ui';
import { cn } from '@/shared/lib/cn';
import { useSettings } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';
import { EngineControls } from '@/features/toggle-engine';

export function HeaderBar() {
  const { data: settings } = useSettings();
  const state = useEngineStore((s) => s.state);
  const connected = useEngineStore((s) => s.connected);

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-4">
      <div className="flex items-center gap-3">
        <span
          className={cn('h-2.5 w-2.5 rounded-full', connected ? 'bg-emerald-400' : 'bg-rose-500')}
          title={connected ? 'Сервер на связи' : 'Нет связи с сервером'}
        />
        <h1 className="text-lg font-semibold text-zinc-100">
          {settings?.assistant.name || 'Ассистент'}
        </h1>
        <StatusBadge state={state} />
      </div>
      <EngineControls />
    </header>
  );
}
