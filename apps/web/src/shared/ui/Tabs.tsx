import { cn } from '@/shared/lib/cn';

export type Tab = { id: string; label: string };

type Props = { tabs: Tab[]; value: string; onChange: (id: string) => void };

// Ретро-вкладки: активная подсвечена фосфором с «диодом» слева.
export function Tabs({ tabs, value, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-1 border-b border-term-border">
      {tabs.map((t) => {
        const active = value === t.id;
        return (
          <button
            key={t.id}
            onClick={() => onChange(t.id)}
            className={cn(
              'inline-flex items-center gap-1.5 border border-b-0 px-3 py-1.5',
              'font-pixel text-[9px] uppercase leading-none transition-colors',
              active
                ? 'border-term-border bg-phosphor/10 text-phosphor text-glow'
                : 'border-transparent text-term-dim hover:text-term-fg',
            )}
          >
            <span className={cn('h-1.5 w-1.5', active ? 'bg-phosphor' : 'bg-term-border')} />
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
