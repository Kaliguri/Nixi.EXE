import type { ReactNode } from 'react';
import { cn } from '@/shared/lib/cn';

type Props = { title?: string; right?: ReactNode; children: ReactNode; className?: string };

// Ретро-«бокс»: рамка терминала, ASCII-маркер заголовка, угловой акцент.
export function Card({ title, right, children, className }: Props) {
  return (
    <section
      className={cn(
        'relative border border-term-border bg-term-panel/70 p-4',
        'before:absolute before:left-[-1px] before:top-[-1px] before:h-2 before:w-2',
        'before:border-l before:border-t before:border-phosphor/70',
        'after:absolute after:bottom-[-1px] after:right-[-1px] after:h-2 after:w-2',
        'after:border-b after:border-r after:border-phosphor/70',
        className,
      )}
    >
      {(title || right) && (
        <header className="mb-3 flex items-center justify-between border-b border-term-border/60 pb-2">
          {title && (
            <h2 className="glitch flex items-center gap-1.5 font-pixel text-[10px] uppercase tracking-wider text-phosphor text-glow-soft">
              <span className="text-term-dim">{'>'}</span>
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
