import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Tabs, type Tab } from '@/shared/ui';
import { LlmSettings } from '@/features/edit-llm-settings';
import { ApiKeys } from '@/features/manage-api-keys';
import { TtsSettings } from '@/features/edit-tts';
import { WakeWordSettings } from '@/features/edit-wakeword';
import { SkillsSettings } from '@/features/edit-skills';
import { AppearanceSettings } from '@/features/edit-appearance';

export function SettingsTabs() {
  const { t } = useTranslation();
  const [tab, setTab] = useState('llm');

  const tabs: Tab[] = [
    { id: 'llm', label: t('tabs.llm') },
    { id: 'tts', label: t('tabs.tts') },
    { id: 'wake', label: t('tabs.wake') },
    { id: 'skills', label: t('tabs.skills') },
    { id: 'keys', label: t('tabs.keys') },
    { id: 'appearance', label: t('tabs.appearance') },
  ];

  return (
    <Card title={t('settings.title')}>
      <Tabs tabs={tabs} value={tab} onChange={setTab} />
      <div className="pt-4">
        {tab === 'llm' && <LlmSettings />}
        {tab === 'tts' && <TtsSettings />}
        {tab === 'wake' && <WakeWordSettings />}
        {tab === 'skills' && <SkillsSettings />}
        {tab === 'keys' && <ApiKeys />}
        {tab === 'appearance' && <AppearanceSettings />}
      </div>
    </Card>
  );
}
