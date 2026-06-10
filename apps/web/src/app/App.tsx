import { useEffect } from 'react';
import { Providers } from './providers';
import { connectEngineSocket } from '@/shared/ws/useEngineSocket';
import { DashboardPage } from '@/pages/dashboard';
import { useCrt, applyCrtClass } from '@/shared/lib/useCrt';
import { useTheme, applyThemeAttr } from '@/shared/lib/useTheme';

export function App() {
  const crt = useCrt((s) => s.on);
  const theme = useTheme((s) => s.theme);

  useEffect(() => {
    connectEngineSocket();
  }, []);

  useEffect(() => {
    applyCrtClass(crt);
  }, [crt]);

  useEffect(() => {
    applyThemeAttr(theme);
  }, [theme]);

  return (
    <Providers>
      <DashboardPage />
    </Providers>
  );
}
