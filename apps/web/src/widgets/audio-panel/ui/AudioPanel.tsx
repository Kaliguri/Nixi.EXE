import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Select, Slider, VUMeter } from '@/shared/ui';
import { useDevices, useSaveSettings, useSettings, type Device } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';
import { useNow } from '@/shared/lib/useNow';
import { useDebouncedCallback } from '@/shared/lib/useDebouncedCallback';

function deviceOptions(list: Device[] | undefined, defaultLabel: string) {
  return [
    { value: '', label: defaultLabel },
    ...(list ?? []).map((d) => ({ value: String(d.id), label: d.name })),
  ];
}

export function AudioPanel() {
  const { t } = useTranslation();
  const { data: settings } = useSettings();
  const { data: devices, refetch, isFetching } = useDevices();
  const save = useSaveSettings();

  const inputDb = useEngineStore((s) => s.inputDb);
  const inputTs = useEngineStore((s) => s.inputTs);
  const outputDb = useEngineStore((s) => s.outputDb);
  const outputTs = useEngineStore((s) => s.outputTs);
  const now = useNow(120);

  // Локальные значения громкости для мгновенного отклика слайдера;
  // запись в config.yaml — дебаунсом, чтобы не писать на каждый тик.
  const [inGain, setInGain] = useState(100);
  const [outGain, setOutGain] = useState(100);
  useEffect(() => {
    if (!settings) return;
    setInGain(Math.round(settings.audio.input_gain * 100));
    setOutGain(Math.round(settings.audio.output_gain * 100));
  }, [settings]);

  const saveInGain = useDebouncedCallback((v: number) =>
    save.mutate({ audio: { input_gain: v / 100 } }),
  );
  const saveOutGain = useDebouncedCallback((v: number) =>
    save.mutate({ audio: { output_gain: v / 100 } }),
  );

  if (!settings) return <Card title={t('audio.title')}>{t('common.loading')}</Card>;

  const a = settings.audio;
  const inActive = now - inputTs < 400;
  const outActive = now - outputTs < 600;

  return (
    <Card
      title={t('audio.title')}
      right={
        <Button variant="ghost" className="px-2 py-1" onClick={() => refetch()}>
          ↻ {isFetching ? '…' : t('audio.refresh')}
        </Button>
      }
    >
      <div className="space-y-5">
        {/* Вход */}
        <div className="space-y-2">
          <Select
            label={t('audio.micInput')}
            value={a.input_device === null ? '' : String(a.input_device)}
            options={deviceOptions(devices?.input, t('audio.systemDefault'))}
            onValueChange={(v) =>
              save.mutate({ audio: { input_device: v === '' ? null : Number(v) } })
            }
          />
          <VUMeter db={inActive ? inputDb : -120} active={inActive} />
          <Slider
            label={t('audio.inputGain')}
            valueLabel={`${inGain}%`}
            min={0}
            max={200}
            step={5}
            value={inGain}
            onValueChange={(v) => {
              setInGain(v);
              saveInGain(v);
            }}
          />
        </div>

        {/* Выход */}
        <div className="space-y-2">
          <Select
            label={t('audio.output')}
            value={a.output_device === null ? '' : String(a.output_device)}
            options={deviceOptions(devices?.output, t('audio.systemDefault'))}
            onValueChange={(v) =>
              save.mutate({ audio: { output_device: v === '' ? null : Number(v) } })
            }
          />
          <VUMeter db={outActive ? outputDb : -120} active={outActive} />
          <Slider
            label={t('audio.outputVolume')}
            valueLabel={`${outGain}%`}
            min={0}
            max={200}
            step={5}
            value={outGain}
            onValueChange={(v) => {
              setOutGain(v);
              saveOutGain(v);
            }}
          />
        </div>
      </div>
    </Card>
  );
}
