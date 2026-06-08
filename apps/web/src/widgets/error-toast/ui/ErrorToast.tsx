import { useEngineStore } from '@/shared/ws/useEngineSocket';

export function ErrorToast() {
  const error = useEngineStore((s) => s.error);
  const dismiss = useEngineStore((s) => s.dismissError);
  if (!error) return null;

  return (
    <div className="fixed bottom-4 left-1/2 z-50 max-w-lg -translate-x-1/2">
      <div className="flex items-start gap-3 rounded-lg border border-rose-800 bg-rose-950/90 px-4 py-3 text-sm text-rose-100 shadow-xl backdrop-blur">
        <span className="mt-0.5">⚠</span>
        <span className="flex-1">{error}</span>
        <button onClick={dismiss} className="text-rose-300 hover:text-white" aria-label="Закрыть">
          ✕
        </button>
      </div>
    </div>
  );
}
