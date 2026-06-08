import { create } from 'zustand';
import { wsUrl } from '@/shared/config';
import { wsEventSchema, type EngineStateName } from '@/shared/api';

export type LogEntry = {
  id: number;
  role: 'user' | 'assistant' | 'system';
  text: string;
  model?: string;
  ts: number;
};

type EngineStore = {
  connected: boolean;
  state: EngineStateName;
  inputDb: number;
  outputDb: number;
  inputTs: number;
  outputTs: number;
  log: LogEntry[];
  error: string | null;
  clearLog: () => void;
  dismissError: () => void;
  _setConnected: (v: boolean) => void;
  _ingest: (raw: unknown) => void;
};

let logSeq = 0;

export const useEngineStore = create<EngineStore>((set) => ({
  connected: false,
  state: 'stopped',
  inputDb: -120,
  outputDb: -120,
  inputTs: 0,
  outputTs: 0,
  log: [],
  error: null,
  clearLog: () => set({ log: [] }),
  dismissError: () => set({ error: null }),
  _setConnected: (v) => set({ connected: v }),
  _ingest: (raw) => {
    const parsed = wsEventSchema.safeParse(raw);
    if (!parsed.success) return;
    const evt = parsed.data;
    switch (evt.type) {
      case 'status':
        set({ state: evt.state });
        break;
      case 'level':
        if (evt.source === 'input') set({ inputDb: evt.db, inputTs: Date.now() });
        else set({ outputDb: evt.db, outputTs: Date.now() });
        break;
      case 'transcript':
        set((s) => ({
          log: [
            ...s.log.slice(-199),
            { id: ++logSeq, role: evt.role, text: evt.text, model: evt.model, ts: Date.now() },
          ],
        }));
        break;
      case 'error':
        set({ error: evt.message });
        break;
    }
  },
}));

let socket: WebSocket | null = null;
let reconnectTimer: number | undefined;

/** Идемпотентно открывает единственное WS-соединение с авто-реконнектом. */
export function connectEngineSocket(): void {
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)
  )
    return;

  const ws = new WebSocket(wsUrl());
  socket = ws;

  ws.onopen = () => useEngineStore.getState()._setConnected(true);
  ws.onmessage = (e) => {
    try {
      useEngineStore.getState()._ingest(JSON.parse(e.data));
    } catch {
      // битый кадр — игнорируем
    }
  };
  ws.onclose = () => {
    useEngineStore.getState()._setConnected(false);
    window.clearTimeout(reconnectTimer);
    reconnectTimer = window.setTimeout(connectEngineSocket, 1500);
  };
  ws.onerror = () => ws.close();
}
