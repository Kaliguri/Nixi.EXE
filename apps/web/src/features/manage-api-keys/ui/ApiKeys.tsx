import { useState } from 'react';
import { Button } from '@/shared/ui';
import { useKeys, useSaveKeys } from '@/shared/api';

const FIELDS = [
  { key: 'ANTHROPIC_API_KEY', label: 'Anthropic (Claude)', hint: 'console.anthropic.com' },
  { key: 'OPENAI_API_KEY', label: 'OpenAI (GPT)', hint: 'platform.openai.com/api-keys' },
] as const;

export function ApiKeys() {
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
      <p className="text-xs text-zinc-500">
        Ключи хранятся локально в <code>.env</code>. Поле показывает только маску текущего ключа —
        введи новый, чтобы заменить, или оставь пустым.
      </p>
      {FIELDS.map((f) => (
        <label key={f.key} className="block">
          <span className="mb-1 flex justify-between text-xs text-zinc-400">
            <span>{f.label}</span>
            <span className="text-zinc-600">
              {data?.[f.key] ? `текущий: ${data[f.key]}` : 'не задан'}
            </span>
          </span>
          <input
            type="password"
            autoComplete="off"
            placeholder={data?.[f.key] ?? 'sk-…'}
            value={draft[f.key] ?? ''}
            onChange={(e) => setDraft((d) => ({ ...d, [f.key]: e.target.value }))}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none"
          />
          <span className="mt-0.5 block text-xs text-zinc-600">{f.hint}</span>
        </label>
      ))}
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? 'Сохраняю…' : 'Сохранить ключи'}
      </Button>
    </div>
  );
}
