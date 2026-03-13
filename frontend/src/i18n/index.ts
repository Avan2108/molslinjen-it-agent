/**
 * i18n exports and utilities
 */

import { en, TranslationKeys } from './en';
import { da } from './da';
import { sv } from './sv';
import { Locale } from '../types';

export type { TranslationKeys };

export const translations: Record<string, TranslationKeys> = {
  en,
  da,
  sv,
};

/**
 * Get translations for a locale
 */
export function getTranslations(locale: Locale | string): TranslationKeys {
  const localeKey = locale === Locale.AUTO ? detectLocale() : locale;
  return translations[localeKey] || translations.en;
}

/**
 * Detect user's preferred locale from browser
 */
export function detectLocale(): string {
  const browserLang = navigator.language.split('-')[0].toLowerCase();
  if (browserLang in translations) {
    return browserLang;
  }
  return 'en';
}

/**
 * Get available locales
 */
export function getAvailableLocales(): { code: string; name: string }[] {
  return [
    { code: 'en', name: 'English' },
    { code: 'da', name: 'Dansk' },
    { code: 'sv', name: 'Svenska' },
  ];
}
