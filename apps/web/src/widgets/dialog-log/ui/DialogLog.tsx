import { useEffect, useRef } from 'react';
import { Button, Card } from '@/shared/ui';
import { cn } from '@/shared/lib/cn';
import { useEngineStore, type LogEntry } from '@/shared/ws/useEngineSocket';
import { PushToTalkButton } from '@/features/push-to-talk';

const roleStyle: Record<LogEntry['role'], { box: string; who: (m?: string) => string }> = {
  user: { box: 'bg-zinc-800/60 text-zinc-100', who: () => 'Ты' },
  assistant: {
    box: 'bg-indigo-950/40 text-indigo-100 border border-indigo-900/50',
    who: (m) => (m ? `Ассистент · ${m}` : 'Ассистент'),
  },
  system: { box: 'bg-transparent text-zinc-500 italic', who: () => 'система' },
};

function timeLabel(ts: number) {
  return new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

export function DialogLog() {
  const log = useEngineStore((s) => s.log);
  const clearLog = useEngineStore((s) => s.clearLog);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (log.length > 0) bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  return (
    <Card
      title="Диалог"
      className="flex min-h-0 flex-col"
      right={
        <div className="flex gap-2">
          <PushToTalkButton />
          <Button variant="ghost" className="px-2 py-1 text-xs" onClick={clearLog}>
            Очистить
          </Button>
        </div>
      }
    >
      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {log.length === 0 && (
          <p className="py-8 text-center text-sm text-zinc-600">
            Пока пусто. Нажми «Старт» и скажи фразу активации (или «Говорить»).
          </p>
        )}
        {log.map((e) => {
          const s = roleStyle[e.role];
          return (
            <div key={e.id} className={cn('rounded-lg px-3 py-2 text-sm', s.box)}>
              <div className="mb-0.5 flex justify-between text-xs text-zinc-500">
                <span>{s.who(e.model)}</span>
                <span className="tabular-nums">{timeLabel(e.ts)}</span>
              </div>
              {e.text}
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </Card>
  );
}
