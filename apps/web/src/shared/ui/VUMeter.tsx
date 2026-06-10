import { cn } from '@/shared/lib/cn';

/** Уровень в dBFS (−120..0) → дискретная «лампочная» шкала из 20 сегментов. */
export function VUMeter({ db, active = true }: { db: number; active?: boolean }) {
  const SEGMENTS = 20;
  // −60 dB = тишина, 0 dB = максимум.
  const pct = Math.max(0, Math.min(100, ((db + 60) / 60) * 100));
  const lit = active ? Math.round((pct / 100) * SEGMENTS) : 0;
  const dbLabel = db <= -119 ? '−∞' : `${Math.round(db)} dB`;

  return (
    <div className="flex items-center gap-2">
      <div className="flex flex-1 gap-px">
        {Array.from({ length: SEGMENTS }, (_, i) => {
          const on = i < lit;
          // Зелёный → жёлтый → красный по мере роста уровня.
          const color =
            i >= SEGMENTS - 3 ? 'bg-danger' : i >= SEGMENTS - 7 ? 'bg-amber' : 'bg-phosphor';
          return (
            <span
              key={i}
              className={cn(
                'h-3 flex-1 transition-opacity duration-75',
                on
                  ? cn(color, 'opacity-100 shadow-[0_0_4px_currentColor]')
                  : 'bg-term-border/50 opacity-40',
              )}
            />
          );
        })}
      </div>
      <span className="w-14 text-right text-xs tabular-nums text-term-dim">{dbLabel}</span>
    </div>
  );
}
