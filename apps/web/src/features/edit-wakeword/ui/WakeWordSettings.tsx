import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Select, Slider, Toggle } from '@/shared/ui';
import { useSaveSettings, useSettings } from '@/shared/api';

export function WakeWordSettings() {
  const { t } = useTranslation();
  const { data } = useSettings();
  const save = useSaveSettings();

  const [mode, setMode] = useState('wakeword');
  const [endMode, setEndMode] = useState('phrase');
  const [endPhrases, setEndPhrases] = useState('');
  const [phrases, setPhrases] = useState('');
  const [fuzzy, setFuzzy] = useState(70);
  const [silence, setSilence] = useState(1.2);
  const [maxSec, setMaxSec] = useState(15);
  const [beep, setBeep] = useState(true);

  useEffect(() => {
    if (!data) return;
    setMode(data.trigger.mode);
    setEndMode(data.trigger.end_mode);
    setEndPhrases(data.trigger.end_phrases.join('\n'));
    setPhrases(data.trigger.wakeword.phrases.join('\n'));
    setFuzzy(Math.round(data.trigger.wakeword.fuzzy * 100));
    setSilence(data.trigger.silence_seconds);
    setMaxSec(data.trigger.max_seconds);
    setBeep(data.trigger.beep);
  }, [data]);

  if (!data) return <p className="text-sm text-term-dim">{t('common.loading')}</p>;

  const onSave = () =>
    save.mutate({
      trigger: {
        mode,
        end_mode: endMode,
        end_phrases: endPhrases
          .split('\n')
          .map((s) => s.trim())
          .filter(Boolean),
        silence_seconds: silence,
        max_seconds: maxSec,
        beep,
        wakeword: {
          phrases: phrases
            .split('\n')
            .map((s) => s.trim())
            .filter(Boolean),
          fuzzy: fuzzy / 100,
        },
      },
    });

  return (
    <div className="max-w-md space-y-4">
      <Select
        label={t('wake.mode')}
        value={mode}
        onValueChange={setMode}
        options={[
          { value: 'wakeword', label: t('wake.modeWake') },
          { value: 'push_to_talk', label: t('wake.modePtt') },
        ]}
      />
      {mode === 'wakeword' && (
        <>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-term-dim">
              {t('wake.phrases')}
            </span>
            <textarea
              value={phrases}
              onChange={(e) => setPhrases(e.target.value)}
              rows={5}
              className="w-full border border-term-border bg-term-panel-2 px-3 py-2 font-mono text-sm text-term-fg transition-colors focus:border-phosphor focus:outline-none"
            />
          </label>
          <Slider
            label={t('wake.fuzzy')}
            valueLabel={`${fuzzy}%`}
            min={40}
            max={95}
            step={5}
            value={fuzzy}
            onValueChange={setFuzzy}
          />
        </>
      )}
      <Select
        label={t('wake.endMode')}
        value={endMode}
        onValueChange={setEndMode}
        options={[
          { value: 'phrase', label: t('wake.endModePhrase') },
          { value: 'silence', label: t('wake.endModeSilence') },
        ]}
      />
      {endMode === 'phrase' ? (
        <label className="block">
          <span className="mb-1 block text-[11px] uppercase tracking-wide text-term-dim">
            {t('wake.endPhrases')}
          </span>
          <textarea
            value={endPhrases}
            onChange={(e) => setEndPhrases(e.target.value)}
            rows={3}
            className="w-full border border-term-border bg-term-panel-2 px-3 py-2 font-mono text-sm text-term-fg transition-colors focus:border-phosphor focus:outline-none"
          />
          <span className="mt-1 block text-xs text-term-dim">{t('wake.endPhrasesHint')}</span>
        </label>
      ) : (
        <Slider
          label={t('wake.silence')}
          valueLabel={`${silence.toFixed(1)} ${t('units.sec')}`}
          min={0.5}
          max={3}
          step={0.1}
          value={silence}
          onValueChange={setSilence}
        />
      )}
      <Slider
        label={t('wake.maxLen')}
        valueLabel={`${maxSec} ${t('units.sec')}`}
        min={5}
        max={30}
        step={1}
        value={maxSec}
        onValueChange={setMaxSec}
      />
      <Toggle checked={beep} onChange={setBeep} label={t('wake.beep')} />
      <p className="text-xs text-amber/80">{t('wake.note')}</p>
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? t('common.saving') : t('common.save')}
      </Button>
    </div>
  );
}
