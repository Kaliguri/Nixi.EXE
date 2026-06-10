import type { ButtonHTMLAttributes } from 'react';
import { cn } from '@/shared/lib/cn';

type Variant = 'primary' | 'ghost' | 'danger' | 'success';

// Ретро-кнопки: квадратные, моноширинные, с «хард»-тенью и вдавливанием.
const variants: Record<Variant, string> = {
  primary: 'bg-coral/15 text-coral border-coral/60 hover:bg-coral/25 hover:text-glow',
  success: 'bg-phosphor/15 text-phosphor border-phosphor/60 hover:bg-phosphor/25 hover:text-glow',
  danger: 'bg-danger/15 text-danger border-danger/60 hover:bg-danger/25 hover:text-glow',
  ghost: 'bg-term-panel text-term-dim border-term-border hover:text-term-fg hover:border-term-dim',
};

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant };

export function Button({ variant = 'primary', className, ...rest }: Props) {
  return (
    <button
      className={cn(
        'retro-press inline-flex items-center justify-center gap-2 border px-4 py-2',
        'text-xs font-medium uppercase tracking-wider',
        'disabled:cursor-not-allowed disabled:opacity-40',
        variants[variant],
        className,
      )}
      {...rest}
    />
  );
}
