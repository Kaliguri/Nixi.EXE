import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Select } from '@/shared/ui';
import { useSaveSettings, useSettings } from '@/shared/api';

// Готовые варианты моделей по провайдеру. Можно выбрать из списка
// (текущее значение из config.yaml добавляется, если его в списке нет).
const MODEL_CATALOG: Record<string, string[]> = {
  anthropic: ['claude-opus-4-8', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001'],
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4.1', 'gpt-4.1-mini'],
  google: ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro'],
};

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
      {keys.map((k) => {
        const provider = data.models[k].provider ?? '';
        const current = models[k] ?? '';
        const catalog = MODEL_CATALOG[provider] ?? [];
        const values = current && !catalog.includes(current) ? [current, ...catalog] : catalog;
        return (
          <Select
            key={k}
            label={t('llm.modelFor', { name: k.toUpperCase() })}
            value={current}
            onValueChange={(v) => setModels((m) => ({ ...m, [k]: v }))}
            options={values.map((v) => ({ value: v, label: v }))}
          />
        );
      })}
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? t('common.saving') : t('common.save')}
      </Button>
    </div>
  );
}
