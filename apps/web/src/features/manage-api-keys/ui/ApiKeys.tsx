import { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Button } from '@/shared/ui';
import { useKeys, useSaveKeys } from '@/shared/api';

const FIELDS = [
  { key: 'ANTHROPIC_API_KEY', label: 'Anthropic (Claude)', hint: 'console.anthropic.com' },
  { key: 'OPENAI_API_KEY', label: 'OpenAI (GPT)', hint: 'platform.openai.com/api-keys' },
] as const;

export function ApiKeys() {
  const { t } = useTranslation();
  const { data } = useKeys();
  const save = useSaveKeys();
  const [draft, setDraft] = useState<Record<string, string>>({});

  const onSave = () => {
    const update = Object.fromEntries(Object.entries(draft).filter(([, v]) => v.trim()));
    if (Object.keys(update).length) save.mutate(update);
    setDraft({});
  };

  return (
    <div className="max-w-md space-y-4">
      <p className="text-xs text-term-dim">
        <Trans i18nKey="keys.note">
          Keys are stored locally in <code className="text-phosphor">.env</code>.
        </Trans>
      </p>
      {FIELDS.map((f) => (
        <label key={f.key} className="block">
          <span className="mb-1 flex justify-between text-[11px] uppercase tracking-wide text-term-dim">
            <span>{f.label}</span>
            <span className="text-term-border">
              {data?.[f.key] ? t('keys.current', { mask: data[f.key] ?? '' }) : t('keys.notSet')}
            </span>
          </span>
          <input
            type="password"
            autoComplete="off"
            placeholder={data?.[f.key] ?? 'sk-…'}
            value={draft[f.key] ?? ''}
            onChange={(e) => setDraft((d) => ({ ...d, [f.key]: e.target.value }))}
            className="w-full border border-term-border bg-term-panel-2 px-3 py-2 font-mono text-sm text-term-fg transition-colors focus:border-phosphor focus:outline-none"
          />
          <span className="mt-0.5 block text-xs text-term-border">{f.hint}</span>
        </label>
      ))}
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? t('common.saving') : t('keys.save')}
      </Button>
    </div>
  );
}
