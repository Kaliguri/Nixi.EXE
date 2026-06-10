import { cn } from '@/shared/lib/cn';

type Props = { checked: boolean; onChange: (v: boolean) => void; label?: string };

// Ретро-тумблер: квадратный «рубильник» [ ON / OFF ] со свечением.
export function Toggle({ checked, onChange, label }: Props) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-term-fg">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          'retro-press relative flex h-6 w-14 items-center border px-0.5 font-pixel text-[7px] uppercase',
          checked
            ? 'justify-start border-phosphor/60 bg-phosphor/10 text-phosphor text-glow'
            : 'justify-end border-term-border bg-term-panel-2 text-term-dim',
        )}
      >
        <span className="px-1">{checked ? 'on' : 'off'}</span>
        <span
          className={cn(
            'absolute top-0.5 bottom-0.5 w-5',
            checked
              ? 'right-0.5 bg-phosphor shadow-[0_0_6px_var(--color-phosphor)]'
              : 'left-0.5 bg-term-border',
          )}
        />
      </button>
      {label}
    </label>
  );
}
