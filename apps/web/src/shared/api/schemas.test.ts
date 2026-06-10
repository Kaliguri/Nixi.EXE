import { describe, expect, it } from 'vitest';
import { settingsSchema, wsEventSchema } from './schemas';

const validSettings = {
  audio: { input_device: null, output_device: 3, input_gain: 1, output_gain: 1.5 },
  assistant: { name: 'Никси', default_model: 'claude', language: 'ru' },
  models: { claude: { provider: 'anthropic', model: 'claude-sonnet-4-6', triggers: ['клод'] } },
  tts: { engine: 'edge', edge_voice: 'ru-RU-SvetlanaNeural', edge_rate: '+0%' },
  trigger: {
    mode: 'wakeword',
    silence_seconds: 1.2,
    max_seconds: 15,
    beep: true,
    wakeword: { phrases: ['никси'], fuzzy: 0.7 },
  },
  skills: { enabled: true },
};

describe('settingsSchema', () => {
  it('parses a valid settings payload', () => {
    expect(() => settingsSchema.parse(validSettings)).not.toThrow();
  });

  it('rejects a payload missing audio', () => {
    const { audio: _audio, ...broken } = validSettings;
    expect(settingsSchema.safeParse(broken).success).toBe(false);
  });
});

describe('wsEventSchema', () => {
  it('discriminates a level event', () => {
    const parsed = wsEventSchema.parse({ type: 'level', source: 'input', db: -12 });
    expect(parsed).toEqual({ type: 'level', source: 'input', db: -12 });
  });

  it('discriminates a transcript event with optional model', () => {
    const parsed = wsEventSchema.parse({ type: 'transcript', role: 'assistant', text: 'привет' });
    expect(parsed.type).toBe('transcript');
  });

  it('rejects an unknown event type', () => {
    expect(wsEventSchema.safeParse({ type: 'nope' }).success).toBe(false);
  });
});
