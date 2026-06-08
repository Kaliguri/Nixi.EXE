import { Button } from '@/shared/ui';
import { useEngineAction } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function PushToTalkButton() {
  const state = useEngineStore((s) => s.state);
  const action = useEngineAction();
  const disabled = ['stopped', 'error'].includes(state) || action.isPending;

  return (
    <Button variant="ghost" disabled={disabled} onClick={() => action.mutate('ptt')}>
      ⏺ Говорить
    </Button>
  );
}
