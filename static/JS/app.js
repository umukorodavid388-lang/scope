// ============================================================
// app.js — UI behavior only. Routing + data rendering now live
// in Django views/templates, not here.
// ============================================================
import { renderAll } from './charts.js';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ---------- Theme ----------
function applyTheme(theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
  $$('.theme-icon').forEach((i) => { i.className = 'bi ' + (theme === 'dark' ? 'bi-moon-stars' : 'bi-sun'); });
  $('#navThemeToggle') && ($('#navThemeToggle').innerHTML = `<i class="bi ${theme === 'dark' ? 'bi-moon-stars' : 'bi-sun'}"></i>`);
  $('#topThemeToggle') && ($('#topThemeToggle').innerHTML = `<i class="bi ${theme === 'dark' ? 'bi-moon-stars' : 'bi-sun'}"></i>`);
  localStorage.setItem('scope.theme', theme);
  if ($('#chartMonthly') || $('#chartRevenue') || $('#chartRevisions') || $('#chartCompletion') || $('#chartGrowth')) {
    renderAll();
  }
}
function toggleTheme() { applyTheme(document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark'); }

// ---------- Toast (for optional client-side notices) ----------
export function toast(title, body, icon = 'bi-check-circle') {
  const container = $('#toastContainer');
  if (!container || !window.bootstrap) return;
  const el = document.createElement('div');
  el.className = 'toast align-items-center';
  el.role = 'alert';
  el.innerHTML = `
    <div class="toast-header">
      <i class="bi ${icon} text-primary me-2"></i>
      <strong class="me-auto">${title}</strong>
      <small class="muted">just now</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body">${body}</div>`;
  container.appendChild(el);
  const t = new bootstrap.Toast(el, { delay: 4000 });
  el.addEventListener('hidden.bs.toast', () => el.remove());
  t.show();
}

// ---------- Sidebar (mobile) ----------
function bindSidebar() {
  const sidebar = $('#sidebar');
  const backdrop = $('#sidebarBackdrop');
  if (!sidebar || !backdrop) return;
  const open = () => { sidebar.classList.add('show'); backdrop.classList.add('show'); };
  const close = () => { sidebar.classList.remove('show'); backdrop.classList.remove('show'); };
  $('#sidebarToggle')?.addEventListener('click', open);
  $('#sidebarClose')?.addEventListener('click', close);
  backdrop.addEventListener('click', close);
}

// ---------- Landing scroll / nav ----------
function bindScroll() {
  const nav = $('#landingNav');
  const scrollTop = $('#scrollTop');
  const landing = $('#landing');

  window.addEventListener('scroll', () => {
    if (nav && landing) nav.classList.toggle('scrolled', window.scrollY > 30);
    if (scrollTop) scrollTop.classList.toggle('show', window.scrollY > 400);
  });

  scrollTop?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const target = a.getAttribute('href');
      if (target.length > 1 && $(target)) {
        e.preventDefault();
        $(target).scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// ---------- Fade-in observer ----------
function bindFadeIn() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.12 });
  $$('.fade-in').forEach((el) => obs.observe(el));
}

// ---------- Date ----------
function setTopDate() {
  const el = $('#topDate');
  if (el) el.textContent = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

// ---------- Init ----------
function init() {
  applyTheme(localStorage.getItem('scope.theme') || 'dark');
  setTopDate();
  bindScroll();
  bindFadeIn();
  bindSidebar();

  $('#navThemeToggle')?.addEventListener('click', toggleTheme);
  $('#topThemeToggle')?.addEventListener('click', toggleTheme);
  $('#notifBtn')?.addEventListener('click', () => toast('Notifications', 'You have pending revision requests.', 'bi-bell'));
}

document.addEventListener('DOMContentLoaded', init);
