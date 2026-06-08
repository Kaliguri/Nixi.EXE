import { cn } from '@/shared/lib/cn';

export type Tab = { id: string; label: string };

type Props = { tabs: Tab[]; value: string; onChange: (id: string) => void };

export function Tabs({ tabs, value, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-1 border-b border-zinc-800">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={cn(
            'rounded-t-lg px-3 py-2 text-sm font-medium transition-colors',
            value === t.id ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200',
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
