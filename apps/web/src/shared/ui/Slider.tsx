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
        <div className="mb-1 flex justify-between text-xs text-zinc-400">
          <span>{label}</span>
          <span className="tabular-nums text-zinc-300">{valueLabel}</span>
        </div>
      )}
      <input
        type="range"
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-zinc-700 accent-indigo-500"
        onChange={(e) => onValueChange?.(Number(e.target.value))}
        {...rest}
      />
    </label>
  );
}
