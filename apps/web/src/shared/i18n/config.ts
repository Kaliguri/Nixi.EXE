import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { en } from './locales/en';
import { ru } from './locales/ru';

export const resources = {
  en: { translation: en },
  ru: { translation: ru },
} as const;

export const SUPPORTED_LANGS = ['ru', 'en'] as const;
export type Lang = (typeof SUPPORTED_LANGS)[number];

// Язык по умолчанию — RU; выбор персистится в localStorage (ключ `lang`).
void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ru',
    supportedLngs: SUPPORTED_LANGS,
    detection: {
      order: ['localStorage'],
      lookupLocalStorage: 'lang',
      caches: ['localStorage'],
    },
    interpolation: { escapeValue: false },
  });

export default i18n;
