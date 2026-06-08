import { useEffect, useState } from 'react';
import { Button, Select, Slider, Toggle } from '@/shared/ui';
import { useSaveSettings, useSettings } from '@/shared/api';

export function WakeWordSettings() {
  const { data } = useSettings();
  const save = useSaveSettings();

  const [mode, setMode] = useState('wakeword');
  const [phrases, setPhrases] = useState('');
  const [fuzzy, setFuzzy] = useState(70);
  const [silence, setSilence] = useState(1.2);
  const [maxSec, setMaxSec] = useState(15);
  const [beep, setBeep] = useState(true);

  useEffect(() => {
    if (!data) return;
    setMode(data.trigger.mode);
    setPhrases(data.trigger.wakeword.phrases.join('\n'));
    setFuzzy(Math.round(data.trigger.wakeword.fuzzy * 100));
    setSilence(data.trigger.silence_seconds);
    setMaxSec(data.trigger.max_seconds);
    setBeep(data.trigger.beep);
  }, [data]);

  if (!data) return <p className="text-sm text-zinc-500">Загрузка…</p>;

  const onSave = () =>
    save.mutate({
      trigger: {
        mode,
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
        label="Режим активации"
        value={mode}
        onValueChange={setMode}
        options={[
          { value: 'wakeword', label: 'Wake word (всегда слушает фразу)' },
          { value: 'push_to_talk', label: 'Push-to-talk (кнопка «Говорить»)' },
        ]}
      />
      {mode === 'wakeword' && (
        <>
          <label className="block">
            <span className="mb-1 block text-xs text-zinc-400">
              Фразы активации (по одной на строку)
            </span>
            <textarea
              value={phrases}
              onChange={(e) => setPhrases(e.target.value)}
              rows={5}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 font-mono text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none"
            />
          </label>
          <Slider
            label="Чувствительность совпадения"
            valueLabel={`${fuzzy}%`}
            min={40}
            max={95}
            step={5}
            value={fuzzy}
            onValueChange={setFuzzy}
          />
        </>
      )}
      <Slider
        label="Пауза = конец команды"
        valueLabel={`${silence.toFixed(1)} с`}
        min={0.5}
        max={3}
        step={0.1}
        value={silence}
        onValueChange={setSilence}
      />
      <Slider
        label="Максимум длины команды"
        valueLabel={`${maxSec} с`}
        min={5}
        max={30}
        step={1}
        value={maxSec}
        onValueChange={setMaxSec}
      />
      <Toggle checked={beep} onChange={setBeep} label="Сигнал после активации" />
      <p className="text-xs text-amber-500/80">
        Смена фразы активации применится после Стоп → Старт (модель загружается при старте).
      </p>
      <Button onClick={onSave} disabled={save.isPending}>
        {save.isPending ? 'Сохраняю…' : 'Сохранить'}
      </Button>
    </div>
  );
}
