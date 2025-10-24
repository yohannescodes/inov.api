const API_PREFIX = window.__API_PREFIX__ ?? `${window.location.origin}/api/v1`;
const TOKEN_KEY = 'novarch-admin-token';

const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const entryForm = document.getElementById('entry-form');
const entriesTableBody = document.querySelector('#entries-table tbody');
const formStatus = document.getElementById('form-status');
const logoutButton = document.getElementById('logout-button');
const resetFormButton = document.getElementById('reset-form');

let token = localStorage.getItem(TOKEN_KEY);

init();

function init() {
  if (token) {
    showDashboard();
    loadEntries();
  } else {
    showLogin();
  }
}

function showLogin() {
  loginView.classList.remove('hidden');
  dashboardView.classList.add('hidden');
}

function showDashboard() {
  loginView.classList.add('hidden');
  dashboardView.classList.remove('hidden');
}

loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginError.textContent = '';

  const formData = new FormData(loginForm);
  const payload = new URLSearchParams();
  payload.append('username', formData.get('email'));
  payload.append('password', formData.get('password'));

  try {
    const response = await fetch(`${API_PREFIX}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: payload,
    });

    if (!response.ok) {
      throw new Error('Invalid credentials');
    }

    const data = await response.json();
    token = data.access_token;
    localStorage.setItem(TOKEN_KEY, token);
    loginForm.reset();
    showDashboard();
    await loadEntries();
  } catch (error) {
    loginError.textContent = error.message ?? 'Unable to login';
  }
});

logoutButton?.addEventListener('click', () => {
  token = null;
  localStorage.removeItem(TOKEN_KEY);
  entriesTableBody.innerHTML = '';
  showLogin();
});

resetFormButton?.addEventListener('click', () => {
  entryForm.reset();
  entryForm.querySelector('[name="entryId"]').value = '';
  formStatus.textContent = '';
});

entryForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!token) {
    formStatus.textContent = 'You must be signed in.';
    return;
  }

  const formData = new FormData(entryForm);
  const entryId = formData.get('entryId');

  const payload = {
    title: formData.get('title'),
    subtitle: emptyToNull(formData.get('subtitle')),
    slug: formData.get('slug'),
    category: formData.get('category'),
    summary: emptyToNull(formData.get('summary')),
    content_html: formData.get('content_html'),
    content_markdown: emptyToNull(formData.get('content_markdown')),
    is_published: formData.get('is_published') === 'on',
    published_at: formatDateTime(formData.get('published_at')),
  };

  const method = entryId ? 'PUT' : 'POST';
  const url = entryId ? `${API_PREFIX}/admin/entries/${entryId}` : `${API_PREFIX}/admin/entries/`;

  formStatus.textContent = 'Saving…';

  try {
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Failed to save entry');
    }

    await loadEntries();
    entryForm.reset();
    entryForm.querySelector('[name="entryId"]').value = '';
    formStatus.textContent = 'Saved.';
  } catch (error) {
    formStatus.textContent = error.message ?? 'Save failed';
  }
});

async function loadEntries() {
  if (!token) return;
  entriesTableBody.innerHTML = '<tr><td colspan="5">Loading…</td></tr>';
  try {
    const response = await fetch(`${API_PREFIX}/admin/entries/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      throw new Error('Unable to fetch entries');
    }

    const entries = await response.json();
    renderEntries(entries);
  } catch (error) {
    entriesTableBody.innerHTML = `<tr><td colspan="5">${error.message}</td></tr>`;
  }
}

function renderEntries(entries) {
  if (!Array.isArray(entries) || entries.length === 0) {
    entriesTableBody.innerHTML = '<tr><td colspan="5">No entries yet.</td></tr>';
    return;
  }

  entriesTableBody.innerHTML = '';
  entries.forEach((entry) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${escapeHtml(entry.title)}</td>
      <td>${entry.category}</td>
      <td>${entry.is_published ? 'Yes' : 'No'}</td>
      <td>${formatDate(entry.updated_at)}</td>
      <td><button data-entry="${entry.id}" class="ghost small">Edit</button></td>
    `;
    entriesTableBody.appendChild(tr);
  });

  entriesTableBody.querySelectorAll('button[data-entry]').forEach((button) => {
    button.addEventListener('click', () => {
      const entryId = button.getAttribute('data-entry');
      const entry = entries.find((item) => item.id === entryId);
      if (!entry) return;
      populateForm(entry);
    });
  });
}

function populateForm(entry) {
  entryForm.querySelector('[name="entryId"]').value = entry.id;
  entryForm.querySelector('[name="title"]').value = entry.title ?? '';
  entryForm.querySelector('[name="subtitle"]').value = entry.subtitle ?? '';
  entryForm.querySelector('[name="slug"]').value = entry.slug ?? '';
  entryForm.querySelector('[name="category"]').value = entry.category ?? 'doctrine';
  entryForm.querySelector('[name="summary"]').value = entry.summary ?? '';
  entryForm.querySelector('[name="content_html"]').value = entry.content_html ?? '';
  entryForm.querySelector('[name="content_markdown"]').value = entry.content_markdown ?? '';
  entryForm.querySelector('[name="is_published"]').checked = Boolean(entry.is_published);
  entryForm.querySelector('[name="published_at"]').value = entry.published_at ? entry.published_at.slice(0, 16) : '';
  formStatus.textContent = `Editing “${entry.title}”`;
}

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value;
  return div.innerHTML;
}

function formatDate(value) {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleString();
  } catch (error) {
    return value;
  }
}

function emptyToNull(value) {
  return value && value.trim().length > 0 ? value : null;
}

function formatDateTime(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}
