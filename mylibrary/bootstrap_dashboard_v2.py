"""Write premium dashboard + updated base.html."""
import os

FILES = {}

# ============ PREMIUM BASE.HTML ============
FILES["app/templates/base.html"] = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}MyLibrary{% endblock %}</title>
  <link rel="preconnect" href="https://cdn.jsdelivr.net">
  <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --navy-950: #060d1f;
      --navy-900: #0b1120;
      --navy-800: #111a2e;
      --navy-700: #1a2540;
      --navy-600: #243356;
      --gold-600: #b8942a;
      --gold-500: #d4af37;
      --gold-400: #e2c25a;
      --gold-300: #f0d980;
      --teal-600: #0d9488;
      --teal-500: #14b8a6;
      --teal-400: #2dd4bf;
      --gray-50: #f8fafc;
      --gray-100: #f1f5f9;
      --gray-200: #e2e8f0;
      --gray-300: #cbd5e1;
      --gray-500: #64748b;
      --gray-700: #334155;
      --danger: #ef4444;
      --success: #10b981;
      --warning: #f59e0b;
      --info: #3b82f6;
      --radius: 14px;
      --shadow-sm: 0 1px 3px rgba(15,23,42,.06);
      --shadow-md: 0 4px 16px rgba(15,23,42,.08);
      --shadow-lg: 0 12px 32px rgba(15,23,42,.12);
      --shadow-glow: 0 0 24px rgba(20,184,166,.25);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Vazirmatn', Tahoma, sans-serif;
      background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
      color: var(--navy-900);
      min-height: 100vh;
      line-height: 1.7;
      -webkit-font-smoothing: antialiased;
    }
    a { color: var(--teal-600); text-decoration: none; transition: color .15s; }
    a:hover { color: var(--teal-500); }

    /* ---- Navbar ---- */
    .navbar {
      position: sticky; top: 0; z-index: 100;
      background: linear-gradient(135deg, var(--navy-950) 0%, var(--navy-800) 100%);
      padding: .9rem 2rem;
      display: flex; align-items: center; justify-content: space-between;
      color: #fff;
      box-shadow: 0 4px 24px rgba(0,0,0,.25);
      backdrop-filter: blur(10px);
      gap: 1rem;
    }
    .navbar::after {
      content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-500), transparent);
    }
    .navbar .brand {
      font-size: 1.4rem; font-weight: 800; letter-spacing: .5px;
      background: linear-gradient(135deg, var(--gold-400), var(--gold-300));
      -webkit-background-clip: text; background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex; align-items: center; gap: .5rem;
      transition: transform .2s;
    }
    .navbar .brand:hover { transform: scale(1.02); }
    .navbar nav { display: flex; gap: .4rem; align-items: center; flex-wrap: wrap; }
    .navbar nav a, .navbar nav button {
      color: #cbd5e1; font-size: .9rem; padding: .45rem .85rem;
      border-radius: 8px; transition: all .2s;
      border: none; background: transparent; cursor: pointer; font-family: inherit;
    }
    .navbar nav a:hover, .navbar nav button:hover {
      background: rgba(255,255,255,.08); color: #fff;
    }
    .role-badge {
      background: linear-gradient(135deg, rgba(212,175,55,.2), rgba(212,175,55,.1));
      color: var(--gold-400);
      padding: .2rem .7rem; border-radius: 999px; font-size: .75rem;
      border: 1px solid rgba(212,175,55,.3);
    }
    .icon-btn {
      position: relative; width: 38px; height: 38px;
      border-radius: 10px; display: inline-flex; align-items: center; justify-content: center;
      background: rgba(255,255,255,.06); color: #cbd5e1; border: none; cursor: pointer;
      transition: all .2s;
    }
    .icon-btn:hover { background: rgba(255,255,255,.12); color: #fff; }
    .badge-dot {
      position: absolute; top: 4px; right: 4px; min-width: 16px; height: 16px;
      background: var(--danger); color: #fff; font-size: .65rem; font-weight: 700;
      border-radius: 999px; display: flex; align-items: center; justify-content: center;
      padding: 0 4px; animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.15); }
    }

    /* ---- Container ---- */
    .container { max-width: 1320px; margin: 2rem auto; padding: 0 1.5rem; }

    /* ---- Cards ---- */
    .card {
      background: #fff; border-radius: var(--radius);
      box-shadow: var(--shadow-md);
      padding: 1.75rem;
      border: 1px solid rgba(226,232,240,.6);
    }
    .card-title { font-size: 1.35rem; margin-bottom: 1.2rem; color: var(--navy-900); font-weight: 700; }

    /* ---- Gradient stat cards ---- */
    .stat-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.1rem; margin-bottom: 1.5rem;
    }
    .stat-card {
      position: relative; overflow: hidden;
      border-radius: var(--radius); padding: 1.4rem;
      background: linear-gradient(135deg, var(--navy-900), var(--navy-700));
      color: #fff; box-shadow: var(--shadow-lg);
      transition: transform .25s ease, box-shadow .25s ease;
      display: flex; flex-direction: column; gap: .4rem;
    }
    .stat-card::before {
      content: ''; position: absolute; top: -30%; right: -30%; width: 60%; height: 60%;
      background: radial-gradient(circle, rgba(212,175,55,.2), transparent 70%);
      pointer-events: none;
    }
    .stat-card:hover {
      transform: translateY(-4px) scale(1.01);
      box-shadow: 0 16px 40px rgba(15,23,42,.2);
    }
    .stat-card.gold { background: linear-gradient(135deg, #b8942a, #d4af37); color: var(--navy-950); }
    .stat-card.teal { background: linear-gradient(135deg, #0d9488, #2dd4bf); }
    .stat-card.blue { background: linear-gradient(135deg, #1e3a8a, #3b82f6); }
    .stat-card.red { background: linear-gradient(135deg, #991b1b, #ef4444); }
    .stat-card.green { background: linear-gradient(135deg, #065f46, #10b981); }
    .stat-card .label {
      font-size: .82rem; opacity: .85; display: flex; align-items: center; gap: .4rem;
    }
    .stat-card .value {
      font-size: 2.2rem; font-weight: 800; letter-spacing: -.5px; line-height: 1.1;
    }
    .stat-card .sub {
      font-size: .75rem; opacity: .75; display: flex; align-items: center; gap: .3rem;
    }

    /* ---- Glass panel ---- */
    .glass {
      background: rgba(255,255,255,.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,.6);
      box-shadow: var(--shadow-md);
      border-radius: var(--radius);
    }

    /* ---- Section title ---- */
    .section-title {
      display: flex; align-items: center; gap: .6rem;
      font-size: 1.2rem; font-weight: 700; color: var(--navy-900);
      margin: 1.75rem 0 1rem;
    }
    .section-title::after {
      content: ''; flex: 1; height: 1px;
      background: linear-gradient(90deg, var(--gray-300), transparent);
    }

    /* ---- Alerts ---- */
    .flash {
      padding: .9rem 1.1rem; border-radius: 10px;
      margin-bottom: 1rem; font-size: .92rem; font-weight: 500;
      display: flex; align-items: center; gap: .6rem;
      animation: slideIn .3s ease;
    }
    @keyframes slideIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
    .flash.success { background: #d1fae5; color: #065f46; border-right: 4px solid var(--success); }
    .flash.danger  { background: #fee2e2; color: #7f1d1d; border-right: 4px solid var(--danger); }
    .flash.warning { background: #fef3c7; color: #78350f; border-right: 4px solid var(--warning); }
    .flash.info    { background: #dbeafe; color: #1e3a8a; border-right: 4px solid var(--info); }

    /* ---- Forms ---- */
    .form-group { margin-bottom: 1.1rem; }
    .form-group label {
      display: block; margin-bottom: .4rem; font-weight: 500;
      color: var(--navy-700); font-size: .9rem;
    }
    .form-control {
      width: 100%; padding: .7rem 1rem;
      border: 1.5px solid var(--gray-200); border-radius: 10px;
      font-family: inherit; font-size: .95rem;
      transition: all .2s;
      background: #fff;
      color: var(--navy-900);
    }
    .form-control:focus {
      outline: none; border-color: var(--teal-500);
      box-shadow: 0 0 0 4px rgba(20,184,166,.12);
    }
    .form-error { color: var(--danger); font-size: .82rem; margin-top: .3rem; display: block; }

    /* ---- Buttons ---- */
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: .4rem;
      padding: .7rem 1.4rem; border: none; border-radius: 10px; cursor: pointer;
      font-family: inherit; font-size: .95rem; font-weight: 600;
      transition: all .2s;
      text-decoration: none;
    }
    .btn:hover { transform: translateY(-1px); }
    .btn:active { transform: translateY(0); }
    .btn-primary {
      background: linear-gradient(135deg, var(--navy-900), var(--navy-700));
      color: #fff; box-shadow: 0 4px 12px rgba(15,23,42,.15);
    }
    .btn-primary:hover { box-shadow: 0 8px 20px rgba(15,23,42,.25); }
    .btn-gold {
      background: linear-gradient(135deg, var(--gold-600), var(--gold-400));
      color: var(--navy-950);
      box-shadow: 0 4px 12px rgba(212,175,55,.25);
    }
    .btn-gold:hover { box-shadow: 0 8px 20px rgba(212,175,55,.4); }
    .btn-teal {
      background: linear-gradient(135deg, var(--teal-600), var(--teal-400));
      color: #fff;
    }
    .btn-ghost {
      background: var(--gray-100); color: var(--navy-900);
    }
    .btn-ghost:hover { background: var(--gray-200); }
    .btn-block { width: 100%; }
    .btn-sm { padding: .35rem .75rem; font-size: .82rem; border-radius: 8px; }

    /* ---- Auth pages ---- */
    .auth-wrap {
      min-height: calc(100vh - 4.5rem); display: flex; align-items: center; justify-content: center;
      padding: 2rem 1rem;
      background:
        radial-gradient(circle at 20% 20%, rgba(20,184,166,.08), transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(212,175,55,.08), transparent 40%);
    }
    .auth-card {
      width: 100%; max-width: 500px;
      background: rgba(255,255,255,.85); backdrop-filter: blur(20px);
      border-radius: 20px; padding: 2.5rem;
      box-shadow: 0 20px 60px rgba(15,23,42,.15);
      border: 1px solid rgba(255,255,255,.7);
    }
    .auth-card h1 { font-size: 1.7rem; color: var(--navy-900); margin-bottom: .3rem; font-weight: 800; }
    .auth-card .subtitle { color: var(--gray-500); font-size: .9rem; margin-bottom: 1.5rem; }

    /* ---- Tables ---- */
    .data-table {
      width: 100%; border-collapse: collapse; font-size: .9rem;
      background: #fff; border-radius: var(--radius); overflow: hidden;
    }
    .data-table thead { background: linear-gradient(135deg, var(--navy-900), var(--navy-700)); color: #fff; }
    .data-table th { padding: .85rem; text-align: right; font-weight: 600; }
    .data-table td { padding: .8rem; border-bottom: 1px solid var(--gray-200); }
    .data-table tbody tr:hover { background: var(--gray-50); }

    /* ---- Badges ---- */
    .chip {
      display: inline-block; padding: .2rem .65rem; border-radius: 999px;
      font-size: .75rem; font-weight: 600;
    }
    .chip-success { background: #d1fae5; color: #065f46; }
    .chip-danger  { background: #fee2e2; color: #7f1d1d; }
    .chip-warning { background: #fef3c7; color: #78350f; }
    .chip-info    { background: #dbeafe; color: #1e3a8a; }
    .chip-muted   { background: var(--gray-100); color: var(--gray-700); }

    /* ---- Error pages ---- */
    .error-page { text-align: center; padding: 5rem 1rem; }
    .error-page h1 {
      font-size: 6rem; line-height: 1; font-weight: 900;
      background: linear-gradient(135deg, var(--gold-500), var(--gold-300));
      -webkit-background-clip: text; background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .error-page p { color: var(--gray-500); margin: 1.2rem 0 2rem; font-size: 1.1rem; }

    /* ---- Scrollbar ---- */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: var(--gray-100); }
    ::-webkit-scrollbar-thumb { background: var(--gray-300); border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--gray-500); }

    /* ---- Responsive ---- */
    @media (max-width: 768px) {
      .navbar { padding: .7rem 1rem; }
      .navbar .brand { font-size: 1.15rem; }
      .container { padding: 0 1rem; margin: 1.2rem auto; }
      .stat-card .value { font-size: 1.8rem; }
      .auth-card { padding: 1.75rem; }
    }
  </style>
</head>
<body>
  <header class="navbar">
    <a href="{{ url_for('web_main.index') }}" class="brand">📚 MyLibrary</a>
    <nav>
      <a href="{{ url_for('web_main.index') }}">خانه</a>
      <a href="{{ url_for('web_books.catalog') }}">کتاب‌ها</a>
      {% if current_user.is_authenticated %}
        {% if current_user.role in ('admin', 'employee') %}
          <a href="{{ url_for('web_borrowings.requests_list') }}">درخواست‌ها</a>
        {% endif %}
        <a href="{{ url_for('web_notifications.list_all') }}" class="icon-btn" title="اعلان‌ها">
          🔔
          <span id="notif-badge" class="badge-dot" style="display:none;">0</span>
        </a>
        <a href="{{ url_for('web_auth.profile') }}" class="role-badge">
          {{ {'student':'دانشجو','employee':'کارمند','admin':'مدیر','guest':'مهمان'}.get(current_user.role, current_user.role) }}
        </a>
        <form action="{{ url_for('web_auth.logout') }}" method="POST" style="display:inline;margin:0;">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
          <button type="submit" class="btn-sm" style="background:transparent;color:#cbd5e1;border:none;cursor:pointer;padding:.45rem .85rem;border-radius:8px;">خروج</button>
        </form>
      {% else %}
        <a href="{{ url_for('web_auth.login') }}">ورود</a>
        <a href="{{ url_for('web_auth.register') }}" class="btn-sm" style="background:linear-gradient(135deg,var(--gold-600),var(--gold-400));color:var(--navy-950);font-weight:600;border-radius:8px;">ثبت‌نام</a>
      {% endif %}
    </nav>
  </header>

  <main class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, msg in messages %}
          <div class="flash {{ category }}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
  </main>

  {% if current_user.is_authenticated %}
  <script>
    // Poll unread notification count every 30s
    async function updateNotifBadge() {
      try {
        const r = await fetch("{{ url_for('web_notifications.api_unread_count') }}");
        if (!r.ok) return;
        const data = await r.json();
        const badge = document.getElementById('notif-badge');
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      } catch (e) {}
    }
    updateNotifBadge();
    setInterval(updateNotifBadge, 30000);
  </script>
  {% endif %}
</body>
</html>
"""

# ============ PREMIUM DASHBOARD ============
FILES["app/templates/dashboard.html"] = """{% extends 'base.html' %}
{% block title %}داشبورد | MyLibrary{% endblock %}
{% block content %}

<!-- Header -->
<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.75rem; flex-wrap:wrap; gap:1rem;">
  <div>
    <h1 style="font-size:2.2rem; font-weight:800; color:var(--navy-900); letter-spacing:-.5px;">داشبورد</h1>
    <p style="color:var(--gray-500); font-size:.95rem; margin-top:.2rem;">
      {% if current_user.is_authenticated %}خوش آمدید، <strong>{{ current_user.full_name }}</strong> 👋{% else %}به کتابخانه هوشمند خوش آمدید{% endif %}
    </p>
  </div>
  <a href="{{ url_for('web_books.catalog') }}" class="btn btn-gold">📚 مشاهده کاتالوگ</a>
</div>

<!-- Stat cards -->
<div class="stat-grid">
  <div class="stat-card">
    <div class="label">📚 کل کتاب‌ها</div>
    <div class="value">{{ stats.total_books }}</div>
    <div class="sub">{{ stats.available_books }} موجود</div>
  </div>
  <div class="stat-card teal">
    <div class="label">📖 امانت‌های فعال</div>
    <div class="value">{{ stats.active_loans }}</div>
    <div class="sub">{{ stats.pending_requests }} در انتظار</div>
  </div>
  <div class="stat-card gold">
    <div class="label">👥 اعضا</div>
    <div class="value">{{ stats.total_users }}</div>
    <div class="sub">{{ stats.total_students }} دانشجو</div>
  </div>
  <div class="stat-card red">
    <div class="label">⏰ تأخیرها</div>
    <div class="value">{{ stats.overdue_loans }}</div>
    <div class="sub">{{ stats.total_reservations }} رزرو فعال</div>
  </div>
</div>

{% if student_stats %}
<div class="section-title">📊 آمار شخصی من</div>
<div class="stat-grid">
  <div class="stat-card green">
    <div class="label">📗 امانت‌های فعال</div>
    <div class="value">{{ student_stats.my_active }}</div>
  </div>
  <div class="stat-card">
    <div class="label">⏳ در انتظار تأیید</div>
    <div class="value">{{ student_stats.my_pending }}</div>
  </div>
  <div class="stat-card red">
    <div class="label">⚠️ تأخیرها</div>
    <div class="value">{{ student_stats.my_overdue }}</div>
  </div>
  <div class="stat-card gold">
    <div class="label">🔖 رزروها</div>
    <div class="value">{{ student_stats.my_reservations }}</div>
  </div>
</div>
{% endif %}

<!-- Charts -->
<div class="section-title">📈 نمودارها</div>
<div style="display:grid; grid-template-columns:2fr 1fr; gap:1.1rem; margin-bottom:1.5rem;">
  <div class="glass" style="padding:1.5rem;">
    <h3 style="margin-bottom:1rem; color:var(--navy-900); font-size:1rem; font-weight:700;">امانت‌های ۷ روز اخیر</h3>
    <canvas id="chart7d" height="110"></canvas>
  </div>
  <div class="glass" style="padding:1.5rem;">
    <h3 style="margin-bottom:1rem; color:var(--navy-900); font-size:1rem; font-weight:700;">توزیع دسته‌ها</h3>
    <canvas id="chartCat" height="200"></canvas>
  </div>
</div>

<!-- Bottom grid -->
<div style="display:grid; grid-template-columns:1fr 1fr; gap:1.1rem;">
  <div class="glass" style="padding:1.5rem;">
    <h3 style="margin-bottom:1rem; color:var(--navy-900); font-size:1rem; font-weight:700;">🏆 محبوب‌ترین کتاب‌ها</h3>
    {% if popular %}
      {% for p in popular %}
        <div style="display:flex; justify-content:space-between; align-items:center; padding:.7rem 0; border-bottom:1px solid var(--gray-200);">
          <div style="display:flex; align-items:center; gap:.6rem;">
            <div style="width:24px;height:24px;border-radius:6px;background:linear-gradient(135deg,var(--gold-600),var(--gold-400));color:var(--navy-950);font-size:.75rem;font-weight:800;display:flex;align-items:center;justify-content:center;">{{ loop.index }}</div>
            <span style="font-weight:500;">{{ p.title }}</span>
          </div>
          <span class="chip chip-success">{{ p.count }} امانت</span>
        </div>
      {% endfor %}
    {% else %}
      <p style="color:var(--gray-500); font-size:.9rem;">هنوز داده‌ای نیست.</p>
    {% endif %}
  </div>

  {% if recent %}
    <div class="glass" style="padding:1.5rem;">
      <h3 style="margin-bottom:1rem; color:var(--navy-900); font-size:1rem; font-weight:700;">🕐 آخرین فعالیت‌ها</h3>
      {% for r in recent %}
        <div style="display:flex; gap:.7rem; padding:.5rem 0; border-bottom:1px solid var(--gray-200); font-size:.85rem;">
          <div style="color:var(--gold-600); font-weight:600; flex-shrink:0;">{{ r.action }}</div>
          <div style="color:var(--gray-500); flex:1;">{{ r.details or '' }}</div>
          <div style="color:var(--gray-500); font-size:.75rem; flex-shrink:0;">{{ r.created_at.strftime('%H:%M') }}</div>
        </div>
      {% endfor %}
    </div>
  {% endif %}
</div>

<!-- Quick actions -->
<div class="section-title">⚡ دسترسی سریع</div>
<div style="display:flex; gap:.7rem; flex-wrap:wrap;">
  <a href="{{ url_for('web_books.catalog') }}" class="btn btn-primary">📚 کاتالوگ</a>
  {% if current_user.is_authenticated %}
    {% if current_user.is_student %}
      <a href="{{ url_for('web_borrowings.my') }}" class="btn btn-gold">📖 امانت‌های من</a>
    {% endif %}
    {% if current_user.role in ('admin', 'employee') %}
      <a href="{{ url_for('web_borrowings.requests_list') }}" class="btn btn-gold">📋 درخواست‌ها</a>
      <a href="{{ url_for('web_borrowings.all_list') }}" class="btn btn-teal">📊 همه امانت‌ها</a>
      <a href="{{ url_for('web_books.manage') }}" class="btn btn-ghost">⚙️ مدیریت</a>
    {% endif %}
    {% if current_user.is_admin %}
      <a href="{{ url_for('web_admin.audit_list') }}" class="btn btn-ghost">📝 Audit Log</a>
    {% endif %}
  {% endif %}
</div>

<script>
  // Chart 7d with gradient
  const ctx7d = document.getElementById('chart7d').getContext('2d');
  const grad = ctx7d.createLinearGradient(0, 0, 0, 300);
  grad.addColorStop(0, 'rgba(20,184,166,0.85)');
  grad.addColorStop(1, 'rgba(20,184,166,0.15)');
  new Chart(ctx7d, {
    type: 'bar',
    data: {
      labels: {{ chart_7d.labels|tojson }},
      datasets: [{
        label: 'درخواست‌ها',
        data: {{ chart_7d.counts|tojson }},
        backgroundColor: grad,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0b1120', padding: 10, cornerRadius: 8,
          titleFont: { family: 'Vazirmatn' }, bodyFont: { family: 'Vazirmatn' },
        }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(203,213,225,.4)' }, ticks: { font: { family: 'Vazirmatn' } } },
        x: { grid: { display: false }, ticks: { font: { family: 'Vazirmatn' } } }
      }
    }
  });

  // Pie with palette
  new Chart(document.getElementById('chartCat'), {
    type: 'doughnut',
    data: {
      labels: {{ chart_cat.labels|tojson }},
      datasets: [{
        data: {{ chart_cat.counts|tojson }},
        backgroundColor: ['#d4af37','#14b8a6','#3b82f6','#ef4444','#8b5cf6','#f59e0b','#10b981','#64748b'],
        borderWidth: 3, borderColor: '#fff',
      }]
    },
    options: {
      cutout: '65%',
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { font: { family: 'Vazirmatn', size: 11 }, padding: 12, boxWidth: 12, boxHeight: 12 } },
        tooltip: { backgroundColor: '#0b1120', padding: 10, cornerRadius: 8, titleFont: { family: 'Vazirmatn' }, bodyFont: { family: 'Vazirmatn' } }
      }
    }
  });
</script>
{% endblock %}
"""

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: premium base.html + dashboard.html written.")
