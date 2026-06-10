import type { SelectHTMLAttributes } from 'react';
import { cn } from '@/shared/lib/cn';

export type Option = { value: string; label: string };

type Props = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> & {
  label?: string;
  options: Option[];
  onValueChange?: (v: string) => void;
};

export function Select({ label, options, onValueChange, className, ...rest }: Props) {
  return (
    <label className="block">
      {label && (
        <span className="mb-1 block text-[11px] uppercase tracking-wide text-term-dim">
          {label}
        </span>
      )}
      <select
        className={cn(
          'w-full border border-term-border bg-term-panel-2 px-3 py-2 font-mono text-sm text-term-fg',
          'transition-colors focus:border-phosphor focus:outline-none focus:text-glow-soft',
          className,
        )}
        onChange={(e) => onValueChange?.(e.target.value)}
        {...rest}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
