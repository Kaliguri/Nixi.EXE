import { Button } from '@/shared/ui';
import { useEngineAction } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function EngineControls() {
  const state = useEngineStore((s) => s.state);
  const action = useEngineAction();
  const running = !['stopped', 'error'].includes(state);
  const paused = state === 'paused';

  return (
    <div className="flex gap-2">
      {running ? (
        <Button variant="danger" disabled={action.isPending} onClick={() => action.mutate('stop')}>
          ◼ Стоп
        </Button>
      ) : (
        <Button
          variant="success"
          disabled={action.isPending}
          onClick={() => action.mutate('start')}
        >
          ▶ Старт
        </Button>
      )}
      {running &&
        (paused ? (
          <Button variant="ghost" onClick={() => action.mutate('resume')}>
            ▸ Продолжить
          </Button>
        ) : (
          <Button variant="ghost" onClick={() => action.mutate('pause')}>
            ⏸ Пауза
          </Button>
        ))}
    </div>
  );
}
