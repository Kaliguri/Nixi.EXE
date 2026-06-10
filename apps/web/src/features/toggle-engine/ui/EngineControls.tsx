import { useTranslation } from 'react-i18next';
import { Button } from '@/shared/ui';
import { useEngineAction } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function EngineControls() {
  const { t } = useTranslation();
  const state = useEngineStore((s) => s.state);
  const action = useEngineAction();
  const running = !['stopped', 'error'].includes(state);
  const paused = state === 'paused';

  return (
    <div className="flex gap-2">
      {running ? (
        <Button variant="danger" disabled={action.isPending} onClick={() => action.mutate('stop')}>
          ◼ {t('engine.stop')}
        </Button>
      ) : (
        <Button
          variant="success"
          disabled={action.isPending}
          onClick={() => action.mutate('start')}
        >
          ▶ {t('engine.start')}
        </Button>
      )}
      {running &&
        (paused ? (
          <Button variant="ghost" onClick={() => action.mutate('resume')}>
            ▸ {t('engine.resume')}
          </Button>
        ) : (
          <Button variant="ghost" onClick={() => action.mutate('pause')}>
            ⏸ {t('engine.pause')}
          </Button>
        ))}
    </div>
  );
}
