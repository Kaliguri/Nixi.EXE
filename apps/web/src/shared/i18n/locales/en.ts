// Английский словарь. Источник типов для ключей перевода (см. i18next.d.ts).
export const en = {
  common: {
    loading: 'Loading…',
    save: 'Save',
    saving: 'Saving…',
    close: 'Close',
  },
  header: {
    assistant: 'Assistant',
    online: 'Server online',
    offline: 'No connection to server',
  },
  engine: {
    start: 'Start',
    stop: 'Stop',
    pause: 'Pause',
    resume: 'Resume',
    ptt: 'Talk',
  },
  status: {
    stopped: 'Stopped',
    loading: 'Booting…',
    listening: 'Listening',
    recording: 'Recording',
    thinking: 'Thinking',
    speaking: 'Speaking',
    paused: 'Paused',
    error: 'Error',
  },
  audio: {
    title: 'Audio',
    refresh: 'Refresh',
    micInput: 'Microphone (input)',
    inputGain: 'Input gain',
    output: 'Speakers / headphones (output)',
    outputVolume: 'Output volume',
    systemDefault: 'System default',
  },
  dialog: {
    title: 'Dialog',
    clear: 'Clear',
    empty: 'Nothing yet. Hit “Start” and say the wake phrase (or “Talk”).',
    you: 'You',
    assistant: 'Assistant',
    system: 'system',
  },
  settings: {
    title: 'Settings',
  },
  tabs: {
    llm: 'Model',
    tts: 'Voice',
    wake: 'Wake-word',
    skills: 'Skills',
    keys: 'Keys',
    appearance: 'Look',
  },
  appearance: {
    theme: 'Color theme',
    themeGreen: 'Phosphor (green)',
    themeAmber: 'Amber (Claude-style)',
    crt: 'CRT mode',
    crtHint: 'Scanlines, vignette, flicker and glow — pure retro.',
  },
  llm: {
    defaultModel: 'Default active model',
    modelFor: 'Model {{name}}',
  },
  tts: {
    engine: 'Synthesis engine',
    engineEdge: 'Edge (neural voice, needs internet)',
    enginePyttsx3: 'pyttsx3 (offline, system)',
    voice: 'Voice',
    rate: 'Speech rate',
    test: 'Test voice',
    testing: 'Playing…',
    testError: 'Playback failed: {{error}}',
  },
  wake: {
    mode: 'Activation mode',
    modeWake: 'Wake word (always listening)',
    modePtt: 'Push-to-talk (“Talk” button)',
    phrases: 'Wake phrases (one per line)',
    fuzzy: 'Match sensitivity',
    silence: 'Pause = end of command',
    maxLen: 'Max command length',
    beep: 'Beep after activation',
    note: 'Changing the wake phrase applies after Stop → Start (model loads at startup).',
  },
  skills: {
    enabled: 'Local skills enabled',
    available: 'Available skills (handled instantly, without calling the model):',
  },
  keys: {
    note: 'Keys are stored locally in <0>.env</0>. The field shows only a mask of the current key — enter a new one to replace it, or leave it empty.',
    current: 'current: {{mask}}',
    notSet: 'not set',
    save: 'Save keys',
  },
  units: {
    sec: 's',
  },
  ui: {
    crt: 'CRT',
    crtTitle: 'CRT mode — scanlines, glow, flicker',
    language: 'Language',
  },
} as const;

// Структура словаря с «широкими» string-листьями — тип для прочих локалей (ru).
type Stringify<T> = { [K in keyof T]: T[K] extends string ? string : Stringify<T[K]> };
export type Translations = Stringify<typeof en>;
