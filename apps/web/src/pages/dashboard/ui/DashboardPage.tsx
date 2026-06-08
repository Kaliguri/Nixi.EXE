import { HeaderBar } from '@/widgets/header-bar';
import { AudioPanel } from '@/widgets/audio-panel';
import { DialogLog } from '@/widgets/dialog-log';
import { SettingsTabs } from '@/widgets/settings-tabs';
import { ErrorToast } from '@/widgets/error-toast';

export function DashboardPage() {
  return (
    <div className="mx-auto flex min-h-full max-w-6xl flex-col gap-4 p-4">
      <HeaderBar />
      <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-[minmax(280px,1fr)_1.4fr]">
        <AudioPanel />
        <DialogLog />
      </div>
      <SettingsTabs />
      <ErrorToast />
    </div>
  );
}
