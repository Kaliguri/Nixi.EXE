import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card } from '@/shared/ui';
import { cn } from '@/shared/lib/cn';
import { useEngineStore, type LogEntry } from '@/shared/ws/useEngineSocket';
import { PushToTalkButton } from '@/features/push-to-talk';

const roleStyle: Record<LogEntry['role'], string> = {
  user: 'border-l-2 border-term-dim bg-term-panel-2/60 text-term-fg',
  assistant: 'border-l-2 border-phosphor/60 bg-phosphor/5 text-term-fg',
  system: 'border-l-2 border-transparent bg-transparent text-term-dim italic',
};

export function DialogLog() {
  const { t, i18n } = useTranslation();
  const log = useEngineStore((s) => s.log);
  const clearLog = useEngineStore((s) => s.clearLog);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (log.length > 0) bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  const locale = i18n.resolvedLanguage === 'en' ? 'en-US' : 'ru-RU';
  const timeLabel = (ts: number) =>
    new Date(ts).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });

  const who = (e: LogEntry) => {
    if (e.role === 'assistant')
      return e.model ? `${t('dialog.assistant')} · ${e.model}` : t('dialog.assistant');
    if (e.role === 'system') return t('dialog.system');
    return t('dialog.you');
  };

  return (
    <Card
      title={t('dialog.title')}
      className="flex min-h-0 flex-col"
      right={
        <div className="flex gap-2">
          <PushToTalkButton />
          <Button variant="ghost" className="px-2 py-1" onClick={clearLog}>
            {t('dialog.clear')}
          </Button>
        </div>
      }
    >
      <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {log.length === 0 && (
          <p className="cursor-blink py-8 text-center text-sm text-term-dim">{t('dialog.empty')}</p>
        )}
        {log.map((e) => (
          <div key={e.id} className={cn('px-3 py-2 text-sm', roleStyle[e.role])}>
            <div className="mb-0.5 flex justify-between text-[11px] uppercase tracking-wide text-term-dim">
              <span>{who(e)}</span>
              <span className="tabular-nums">{timeLabel(e.ts)}</span>
            </div>
            {e.text}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </Card>
  );
}
