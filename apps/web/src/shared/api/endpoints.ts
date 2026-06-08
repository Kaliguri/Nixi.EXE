import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';
import { api } from './client';
import {
  devicesSchema,
  engineStateSchema,
  keysSchema,
  settingsSchema,
  skillsSchema,
  voicesSchema,
  type Settings,
} from './schemas';

const okSchema = z.object({ ok: z.boolean() });

// Частичное обновление настроек — повторяет вложенность Settings, но всё необязательно.
export type SettingsUpdate = {
  audio?: Partial<Settings['audio']>;
  assistant?: Partial<Settings['assistant']>;
  models?: Record<string, { model?: string }>;
  tts?: Partial<Settings['tts']>;
  trigger?: {
    mode?: string;
    silence_seconds?: number;
    max_seconds?: number;
    beep?: boolean;
    wakeword?: { phrases?: string[]; fuzzy?: number };
  };
  skills?: { enabled?: boolean };
};

export type KeysUpdate = {
  ANTHROPIC_API_KEY?: string;
  OPENAI_API_KEY?: string;
};

// --- Queries ---
export const useDevices = () =>
  useQuery({ queryKey: ['devices'], queryFn: () => api.get('/devices', devicesSchema) });

export const useSettings = () =>
  useQuery({ queryKey: ['settings'], queryFn: () => api.get('/settings', settingsSchema) });

export const useKeys = () =>
  useQuery({ queryKey: ['keys'], queryFn: () => api.get('/keys', keysSchema) });

export const useVoices = () =>
  useQuery({
    queryKey: ['voices'],
    queryFn: () => api.get('/voices', voicesSchema),
    staleTime: Infinity,
  });

export const useSkills = () =>
  useQuery({ queryKey: ['skills'], queryFn: () => api.get('/skills', skillsSchema) });

export const useEngineState = () =>
  useQuery({ queryKey: ['state'], queryFn: () => api.get('/state', engineStateSchema) });

// --- Mutations ---
export const useEngineAction = () =>
  useMutation({
    mutationFn: (action: 'start' | 'stop' | 'pause' | 'resume' | 'ptt') =>
      api.post(`/engine/${action}`, engineStateSchema),
  });

export const useSaveSettings = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (update: SettingsUpdate) => api.put('/settings', settingsSchema, update),
    onSuccess: (data) => qc.setQueryData(['settings'], data),
  });
};

export const useSaveKeys = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (update: KeysUpdate) => api.put('/keys', keysSchema, update),
    onSuccess: (data) => qc.setQueryData(['keys'], data),
  });
};

export const useTestTts = () =>
  useMutation({
    mutationFn: (text?: string) => api.post('/tts/test', okSchema, text ? { text } : {}),
  });
