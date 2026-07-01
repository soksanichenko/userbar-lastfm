'use strict';

const i18n = {
    en: {
        page_title: 'Last.fm UserBar Generator',
        username_label: 'Last.fm Username',
        username_placeholder: 'e.g. ZelGray',
        username_required: 'Username is required',
        username_failed: 'Validation request failed',
        username_invalid: 'Invalid username',
        inner_color: 'Inner color',
        outer_color: 'Outer color',
        text_color: 'Text color',
        border_color: 'Border color',
        logo_color: 'Logo color',
        truncate_text: 'Truncate image to 750px',
        generate_btn: 'Generate userbar',
        result_title: 'YOUR USERBAR',
        direct_link: 'Direct link',
        bb_code: 'BB-code',
        bb_code_link: 'BB-code + profile link',
        html: 'HTML',
        html_link: 'HTML + profile link',
        copy: 'Copy',
        copied: 'Copied!',
        landing_title: 'Last.fm UserBar',
        landing_subtitle: "Generate a live userbar image showing what you're scrobbling on Last.fm.",
        landing_btn: 'Open Generator',
    },
    uk: {
        page_title: 'Генератор UserBar для Last.fm',
        username_label: 'Нікнейм на Last.fm',
        username_placeholder: 'напр. ZelGray',
        username_required: 'Введіть нікнейм',
        username_failed: 'Помилка перевірки',
        username_invalid: 'Невірний нікнейм',
        inner_color: 'Внутрішній колір',
        outer_color: 'Зовнішній колір',
        text_color: 'Колір тексту',
        border_color: 'Колір рамки',
        logo_color: 'Колір логотипу',
        truncate_text: 'Обрізати до 750px',
        generate_btn: 'Згенерувати userbar',
        result_title: 'ВАШ USERBAR',
        direct_link: 'Пряме посилання',
        bb_code: 'BB-код',
        bb_code_link: 'BB-код + посилання на профіль',
        html: 'HTML',
        html_link: 'HTML + посилання на профіль',
        copy: 'Копіювати',
        copied: 'Скопійовано!',
        landing_title: 'Last.fm UserBar',
        landing_subtitle: 'Генеруйте userbar-зображення, що показує, що ви зараз слухаєте на Last.fm.',
        landing_btn: 'Відкрити генератор',
    },
    ru: {
        page_title: 'Генератор UserBar для Last.fm',
        username_label: 'Никнейм на Last.fm',
        username_placeholder: 'напр. ZelGray',
        username_required: 'Введите никнейм',
        username_failed: 'Ошибка проверки',
        username_invalid: 'Неверный никнейм',
        inner_color: 'Внутренний цвет',
        outer_color: 'Внешний цвет',
        text_color: 'Цвет текста',
        border_color: 'Цвет рамки',
        logo_color: 'Цвет логотипа',
        truncate_text: 'Обрезать до 750px',
        generate_btn: 'Сгенерировать userbar',
        result_title: 'ВАШ USERBAR',
        direct_link: 'Прямая ссылка',
        bb_code: 'BB-код',
        bb_code_link: 'BB-код + ссылка на профиль',
        html: 'HTML',
        html_link: 'HTML + ссылка на профиль',
        copy: 'Копировать',
        copied: 'Скопировано!',
        landing_title: 'Last.fm UserBar',
        landing_subtitle: 'Генерируйте userbar-изображение, показывающее, что вы слушаете на Last.fm.',
        landing_btn: 'Открыть генератор',
    },
};

let currentLang = 'en';

function t(key) {
    return (i18n[currentLang] || i18n.en)[key] || key;
}

function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
}

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    document.documentElement.lang = lang;
    applyI18n();
}

function detectLang() {
    const supported = ['en', 'uk', 'ru'];
    for (const locale of navigator.languages || [navigator.language]) {
        const tag = locale.split('-')[0].toLowerCase();
        if (supported.includes(tag)) return tag;
    }
    return 'en';
}

(function init() {
    const saved = localStorage.getItem('lang') || detectLang();
    const select = document.getElementById('lang-select');
    if (select) select.value = saved;
    setLang(saved);
})();
