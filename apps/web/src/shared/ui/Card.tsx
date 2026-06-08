import type { ReactNode } from 'react';
import { cn } from '@/shared/lib/cn';

type Props = { title?: string; right?: ReactNode; children: ReactNode; className?: string };

export function Card({ title, right, children, className }: Props) {
  return (
    <section className={cn('rounded-xl border border-zinc-800 bg-zinc-900/60 p-4', className)}>
      {(title || right) && (
        <header className="mb-3 flex items-center justify-between">
          {title && (
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              {title}
            </h2>
          )}
          {right}
        </header>
      )}
      {children}
    </section>
  );
}
