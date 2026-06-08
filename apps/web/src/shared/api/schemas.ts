import { z } from 'zod';

// --- Устройства ---
export const deviceSchema = z.object({
  id: z.number(),
  name: z.string(),
  samplerate: z.number(),
  channels: z.number(),
  default: z.boolean(),
});
export type Device = z.infer<typeof deviceSchema>;

export const devicesSchema = z.object({
  input: z.array(deviceSchema),
  output: z.array(deviceSchema),
});
export type Devices = z.infer<typeof devicesSchema>;

// --- Состояние движка ---
export const engineStateSchema = z.object({
  state: z.enum([
    'stopped',
    'loading',
    'listening',
    'recording',
    'thinking',
    'speaking',
    'paused',
    'error',
  ]),
});
export type EngineStateName = z.infer<typeof engineStateSchema>['state'];

// --- Настройки ---
export const audioSettingsSchema = z.object({
  input_device: z.number().nullable(),
  output_device: z.number().nullable(),
  input_gain: z.number(),
  output_gain: z.number(),
});

export const modelSettingsSchema = z.object({
  provider: z.string().nullable(),
  model: z.string().nullable(),
  triggers: z.array(z.string()),
});

export const settingsSchema = z.object({
  audio: audioSettingsSchema,
  assistant: z.object({
    name: z.string(),
    default_model: z.string(),
    language: z.string(),
  }),
  models: z.record(z.string(), modelSettingsSchema),
  tts: z.object({
    engine: z.string(),
    edge_voice: z.string(),
    edge_rate: z.string(),
  }),
  trigger: z.object({
    mode: z.string(),
    silence_seconds: z.number(),
    max_seconds: z.number(),
    beep: z.boolean(),
    wakeword: z.object({
      phrases: z.array(z.string()),
      fuzzy: z.number(),
    }),
  }),
  skills: z.object({ enabled: z.boolean() }),
});
export type Settings = z.infer<typeof settingsSchema>;

// --- Ключи (маскированно) ---
export const keysSchema = z.object({
  ANTHROPIC_API_KEY: z.string().nullable(),
  OPENAI_API_KEY: z.string().nullable(),
});
export type Keys = z.infer<typeof keysSchema>;

// --- Голоса TTS ---
export const voiceSchema = z.object({
  short_name: z.string(),
  gender: z.string(),
  name: z.string(),
});
export const voicesSchema = z.array(voiceSchema);
export type Voice = z.infer<typeof voiceSchema>;

// --- Скиллы ---
export const skillsSchema = z.object({
  enabled: z.boolean(),
  skills: z.array(z.object({ name: z.string() })),
});
export type SkillsInfo = z.infer<typeof skillsSchema>;

// --- События WebSocket ---
export const wsEventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('status'), state: engineStateSchema.shape.state }),
  z.object({
    type: z.literal('level'),
    source: z.enum(['input', 'output']),
    db: z.number(),
  }),
  z.object({
    type: z.literal('transcript'),
    role: z.enum(['user', 'assistant', 'system']),
    text: z.string(),
    model: z.string().optional(),
  }),
  z.object({ type: z.literal('error'), message: z.string() }),
]);
export type WsEvent = z.infer<typeof wsEventSchema>;
