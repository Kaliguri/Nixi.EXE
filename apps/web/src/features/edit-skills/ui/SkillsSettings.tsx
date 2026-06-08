import { Toggle } from '@/shared/ui';
import { useSaveSettings, useSkills } from '@/shared/api';

export function SkillsSettings() {
  const { data } = useSkills();
  const save = useSaveSettings();

  if (!data) return <p className="text-sm text-zinc-500">Загрузка…</p>;

  return (
    <div className="max-w-md space-y-4">
      <Toggle
        checked={data.enabled}
        onChange={(v) => save.mutate({ skills: { enabled: v } })}
        label="Локальные скиллы включены"
      />
      <div>
        <p className="mb-2 text-xs text-zinc-400">
          Доступные скиллы (обрабатываются мгновенно, без обращения к нейросети):
        </p>
        <ul className="space-y-1">
          {data.skills.map((s) => (
            <li
              key={s.name}
              className="rounded-lg border border-zinc-800 bg-zinc-800/50 px-3 py-2 text-sm text-zinc-200"
            >
              {s.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
