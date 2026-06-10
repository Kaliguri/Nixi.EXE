import { useTranslation } from 'react-i18next';
import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function ErrorToast() {
  const { t } = useTranslation();
  const error = useEngineStore((s) => s.error);
  const dismiss = useEngineStore((s) => s.dismissError);
  if (!error) return null;

  return (
    <div className="fixed bottom-4 left-1/2 z-50 max-w-lg -translate-x-1/2">
      <div className="flex items-start gap-3 border border-danger bg-term-panel px-4 py-3 text-sm text-danger shadow-[0_0_16px_rgba(255,92,87,0.3)]">
        <span className="mt-0.5">⚠</span>
        <span className="flex-1 text-term-fg">{error}</span>
        <button
          onClick={dismiss}
          className="text-danger transition-colors hover:text-glow"
          aria-label={t('common.close')}
        >
          ✕
        </button>
      </div>
    </div>
  );
}
