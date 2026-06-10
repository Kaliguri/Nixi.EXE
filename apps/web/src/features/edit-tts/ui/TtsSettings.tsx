import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Select, Slider } from '@/shared/ui';
import { useSaveSettings, useSettings, useTestTts, useVoices } from '@/shared/api';

export function TtsSettings() {
  const { t } = useTranslation();
  const { data } = useSettings();
  const { data: voices } = useVoices();
  const save = useSaveSettings();
  const test = useTestTts();

  const [engine, setEngine] = useState('edge');
  const [voice, setVoice] = useState('');
  const [rate, setRate] = useState(0); // проценты −50..+50

  useEffect(() => {
    if (!data) return;
    setEngine(data.tts.engine);
    setVoice(data.tts.edge_voice);
    setRate(parseInt(data.tts.edge_rate.replace('%', ''), 10) || 0);
  }, [data]);

  if (!data) return <p className="text-sm text-term-dim">{t('common.loading')}</p>;

  const rateStr = `${rate >= 0 ? '+' : ''}${rate}%`;
  const onSave = () => save.mutate({ tts: { engine, edge_voice: voice, edge_rate: rateStr } });

  const voiceOptions =
    voices?.map((v) => ({ value: v.short_name, label: `${v.name} (${v.gender})` })) ?? [];
  // Текущий голос может отсутствовать в списке — добавим, чтобы select его показал.
  if (voice && !voiceOptions.some((o) => o.value === voice))
    voiceOptions.unshift({ value: voice, label: voice });

  return (
    <div className="max-w-md space-y-4">
      <Select
        label={t('tts.engine')}
        value={engine}
        onValueChange={setEngine}
        options={[
          { value: 'edge', label: t('tts.engineEdge') },
          { value: 'pyttsx3', label: t('tts.enginePyttsx3') },
        ]}
      />
      {engine === 'edge' && (
        <>
          <Select
            label={t('tts.voice')}
            value={voice}
            onValueChange={setVoice}
            options={voiceOptions.length ? voiceOptions : [{ value: voice, label: voice }]}
          />
          <Slider
            label={t('tts.rate')}
            valueLabel={rateStr}
            min={-50}
            max={50}
            step={5}
            value={rate}
            onValueChange={setRate}
          />
        </>
      )}
      <div className="flex gap-2">
        <Button onClick={onSave} disabled={save.isPending}>
          {save.isPending ? t('common.saving') : t('common.save')}
        </Button>
        <Button variant="ghost" onClick={() => test.mutate(undefined)} disabled={test.isPending}>
          {test.isPending ? `▸ ${t('tts.testing')}` : `► ${t('tts.test')}`}
        </Button>
      </div>
      {test.isError && (
        <p className="text-xs text-danger">{t('tts.testError', { error: String(test.error) })}</p>
      )}
    </div>
  );
}
