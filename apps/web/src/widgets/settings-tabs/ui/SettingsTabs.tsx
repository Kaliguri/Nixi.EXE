import { useState } from 'react';
import { Card, Tabs, type Tab } from '@/shared/ui';
import { LlmSettings } from '@/features/edit-llm-settings';
import { ApiKeys } from '@/features/manage-api-keys';
import { TtsSettings } from '@/features/edit-tts';
import { WakeWordSettings } from '@/features/edit-wakeword';
import { SkillsSettings } from '@/features/edit-skills';

const TABS: Tab[] = [
  { id: 'llm', label: 'Нейросеть' },
  { id: 'tts', label: 'Голос' },
  { id: 'wake', label: 'Wake-word' },
  { id: 'skills', label: 'Скиллы' },
  { id: 'keys', label: 'Ключи' },
];

export function SettingsTabs() {
  const [tab, setTab] = useState('llm');

  return (
    <Card title="Настройки">
      <Tabs tabs={TABS} value={tab} onChange={setTab} />
      <div className="pt-4">
        {tab === 'llm' && <LlmSettings />}
        {tab === 'tts' && <TtsSettings />}
        {tab === 'wake' && <WakeWordSettings />}
        {tab === 'skills' && <SkillsSettings />}
        {tab === 'keys' && <ApiKeys />}
      </div>
    </Card>
  );
}
