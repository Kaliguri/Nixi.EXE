import { useTranslation } from 'react-i18next';
import { Toggle } from '@/shared/ui';
import { useSaveSettings, useSkills } from '@/shared/api';

export function SkillsSettings() {
  const { t } = useTranslation();
  const { data } = useSkills();
  const save = useSaveSettings();

  if (!data) return <p className="text-sm text-term-dim">{t('common.loading')}</p>;

  return (
    <div className="max-w-md space-y-4">
      <Toggle
        checked={data.enabled}
        onChange={(v) => save.mutate({ skills: { enabled: v } })}
        label={t('skills.enabled')}
      />
      <div>
        <p className="mb-2 text-[11px] uppercase tracking-wide text-term-dim">
          {t('skills.available')}
        </p>
        <ul className="space-y-1">
          {data.skills.map((s) => (
            <li
              key={s.name}
              className="border-l-2 border-phosphor/40 bg-term-panel-2/60 px-3 py-2 font-mono text-sm text-term-fg"
            >
              <span className="text-phosphor">$</span> {s.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
