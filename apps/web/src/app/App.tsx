import { useEffect } from 'react';
import { Providers } from './providers';
import { connectEngineSocket } from '@/shared/ws/useEngineSocket';
import { DashboardPage } from '@/pages/dashboard';

export function App() {
  useEffect(() => {
    connectEngineSocket();
  }, []);

  return (
    <Providers>
      <DashboardPage />
    </Providers>
  );
}
