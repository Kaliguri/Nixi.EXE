import { cn } from '@/shared/lib/cn';

/** Уровень в dBFS (−120..0) → горизонтальная полоса. */
export function VUMeter({ db, active = true }: { db: number; active?: boolean }) {
  // −60 dB = тишина, 0 dB = максимум.
  const pct = Math.max(0, Math.min(100, ((db + 60) / 60) * 100));
  const dbLabel = db <= -119 ? '−∞' : `${Math.round(db)} dB`;
  return (
    <div className="flex items-center gap-2">
      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-zinc-800">
        <div
          className={cn(
            'h-full rounded-full transition-[width] duration-75',
            active ? 'bg-gradient-to-r from-emerald-500 via-lime-400 to-rose-500' : 'bg-zinc-600',
          )}
          style={{ width: `${active ? pct : 0}%` }}
        />
      </div>
      <span className="w-14 text-right text-xs tabular-nums text-zinc-400">{dbLabel}</span>
    </div>
  );
}
