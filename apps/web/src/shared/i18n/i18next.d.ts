import 'i18next';
import type { en } from './locales/en';

// Типизация ключей перевода: автокомплит и проверка опечаток в t('...').
declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: { translation: typeof en };
  }
}
