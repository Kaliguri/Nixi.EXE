import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Select } from '@/shared/ui';
import { useSaveSettings, useSettings } from '@/shared/api';

export function LlmSettings() {
  const { t } = useTranslation();
  const { data } = useSettings();
  const save = useSaveSettings();
  const [defaultModel, setDefaultModel] = useState('');
  const [models, setModels] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!data) return;
    setDefaultModel(data.assistant.default_model);
    setModels(Object.fromEntries(Object.entries(data.models).map(([k, v]) => [k, v.model ?? ''])));
  }, [data]);

  if (!data) return <p className="text-sm text-term-dim">{t('common.loading')}</p>;

  const keys = Object.keys(data.models);

  const onSave = () =>
    save.mutate({
      assistant: { default_model: defaultModel },
      models: Object.fromEntries(keys.map((k) => [k, { model: models[k] }])),
    });

  return (
    <div className="max-w-md space-y-4">
      <Select
        label={t('llm.defaultModel')}
        value={defaultModel}
        onValueChange={setDefaultModel}
        options={keys.map((k) => ({
          value: k,
          label: `${k.toUpperCase()} (${data.models[k].provider})`,
        }))}
      />
      {keys.map((k) => (
        <label key={k} className="block">
          <span className="mb-1 block text-[11px] uppercase tracking-wide text-term-dim">
            {t('llm.modelFor', { name: k.toUpperCase() })}
          </span>
          <input
            value={models[k] ?? ''}
            onChange={(e) => setModels((m) => ({ ...m, [k]: e.target.value }))}
            className="w-full border border-term-border bg-term-panel-2 px-3 py-2 font-mono text-sm text-term-fg transition-colors focus:border-phosphor focus:outline-none"
          />
        </label>
      ))}
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? t('common.saving') : t('common.save')}
      </Button>
    </div>
  );
}
