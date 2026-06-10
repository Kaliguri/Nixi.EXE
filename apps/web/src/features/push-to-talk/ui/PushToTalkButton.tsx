import { useTranslation } from 'react-i18next';
import { Button } from '@/shared/ui';
import { useEngineAction } from '@/shared/api';
import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function PushToTalkButton() {
  const { t } = useTranslation();
  const state = useEngineStore((s) => s.state);
  const action = useEngineAction();
  const disabled = ['stopped', 'error'].includes(state) || action.isPending;

  return (
    <Button variant="ghost" disabled={disabled} onClick={() => action.mutate('ptt')}>
      ⏺ {t('engine.ptt')}
    </Button>
  );
}
