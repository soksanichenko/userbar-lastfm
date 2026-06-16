'use strict';

const VALIDATE_DEBOUNCE_MS = 500;
let _usernameValid = false;

function hexToRgbStr(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r}_${g}_${b}`;
}

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function buildUrl(username) {
    const parts = [
        `inner_color=${hexToRgbStr(document.getElementById('inner_color').value)}`,
        `outer_color=${hexToRgbStr(document.getElementById('outer_color').value)}`,
        `text_color=${hexToRgbStr(document.getElementById('text_color').value)}`,
    ];
    if (document.getElementById('enable_border').checked) {
        parts.push(`border_color=${hexToRgbStr(document.getElementById('border_color').value)}`);
    }
    if (document.getElementById('enable_logo').checked) {
        parts.push(`logo_color=${hexToRgbStr(document.getElementById('logo_color').value)}`);
    }
    if (document.getElementById('truncate_text').checked) {
        parts.push('truncate_text=True');
    }
    const encoded = encodeURIComponent(parts.join('&'));
    return `${ROOT_URL}${encodeURIComponent(username)}/${encoded}/userbar.png`;
}

function togglePicker(pickerId, checkbox) {
    document.getElementById(pickerId).disabled = !checkbox.checked;
}

function setValidationState(state, message = '') {
    const spinner = document.getElementById('username-spinner');
    const ok = document.getElementById('username-ok');
    const err = document.getElementById('username-err');
    const feedback = document.getElementById('username-feedback');
    const input = document.getElementById('username');

    spinner.classList.add('d-none');
    ok.classList.add('d-none');
    err.classList.add('d-none');
    feedback.classList.add('d-none');
    input.classList.remove('is-valid', 'is-invalid');

    if (state === 'loading') {
        spinner.classList.remove('d-none');
        _usernameValid = false;
    } else if (state === 'valid') {
        ok.classList.remove('d-none');
        input.classList.add('is-valid');
        _usernameValid = true;
    } else if (state === 'invalid') {
        err.classList.remove('d-none');
        input.classList.add('is-invalid');
        feedback.textContent = message;
        feedback.classList.remove('d-none');
        _usernameValid = false;
    } else {
        _usernameValid = false;
    }
}

const validateUsername = debounce(async (username) => {
    if (!username) {
        setValidationState('');
        return;
    }
    setValidationState('loading');
    try {
        const resp = await fetch(`/api/validate?username=${encodeURIComponent(username)}`);
        const data = await resp.json();
        setValidationState(data.valid ? 'valid' : 'invalid', data.error ?? t('username_invalid'));
    } catch {
        setValidationState('invalid', t('username_failed'));
    }
}, VALIDATE_DEBOUNCE_MS);

async function generate() {
    const username = document.getElementById('username').value.trim();
    if (!username) {
        setValidationState('invalid', t('username_required'));
        return;
    }
    if (!_usernameValid) {
        setValidationState('invalid', t('username_invalid'));
        return;
    }

    const url = buildUrl(username);
    const profileUrl = `https://www.last.fm/user/${encodeURIComponent(username)}`;

    document.getElementById('result-url').value = url;
    document.getElementById('result-bb').value = `[img]${url}[/img]`;
    document.getElementById('result-bb-link').value = `[url=${profileUrl}][img]${url}[/img][/url]`;
    document.getElementById('result-html').value = `<img src="${url}">`;
    document.getElementById('result-html-link').value = `<a href="${profileUrl}"><img src="${url}"></a>`;

    document.getElementById('result-img').src = url;
    document.getElementById('result-profile-link').href = profileUrl;
    document.getElementById('result-section').classList.remove('d-none');
    document.getElementById('result-section').scrollIntoView({behavior: 'smooth', block: 'nearest'});
}

async function copyField(inputId) {
    const input = document.getElementById(inputId);
    const btn = input.nextElementSibling;
    try {
        await navigator.clipboard.writeText(input.value);
    } catch {
        input.select();
        document.execCommand('copy');
    }
    btn.textContent = t('copied');
    btn.classList.add('copied');
    setTimeout(() => {
        btn.textContent = t('copy');
        btn.classList.remove('copied');
    }, 1500);
}

document.getElementById('username').addEventListener('input', (e) => {
    validateUsername(e.target.value.trim());
});

// Validate the pre-filled default username on page load.
validateUsername(document.getElementById('username').value.trim());
