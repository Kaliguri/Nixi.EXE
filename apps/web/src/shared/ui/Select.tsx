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
      {label && <span className="mb-1 block text-xs text-zinc-400">{label}</span>}
      <select
        className={cn(
          'w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100',
          'focus:border-indigo-500 focus:outline-none',
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
