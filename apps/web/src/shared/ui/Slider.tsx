import type { InputHTMLAttributes } from 'react';

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> & {
  label?: string;
  valueLabel?: string;
  onValueChange?: (v: number) => void;
};

export function Slider({ label, valueLabel, onValueChange, ...rest }: Props) {
  return (
    <label className="block">
      {(label || valueLabel) && (
        <div className="mb-1 flex justify-between text-[11px] uppercase tracking-wide text-term-dim">
          <span>{label}</span>
          <span className="tabular-nums text-phosphor text-glow-soft">{valueLabel}</span>
        </div>
      )}
      <input
        type="range"
        className="w-full"
        onChange={(e) => onValueChange?.(Number(e.target.value))}
        {...rest}
      />
    </label>
  );
}
