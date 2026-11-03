"""Write dashboard UI templates."""
import os

FILES = {}

FILES["app/templates/dashboard.html"] = """{% extends 'base.html' %}
{% block title %}داشبورد | MyLibrary{% endblock %}
{% block content %}
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:1rem;">
  <div>
    <h1 style="font-size:2rem; color:var(--navy-900);">داشبورد</h1>
    <p style="color:var(--gray-500);">خوش آمدید{% if current_user.is_authenticated %}، {{ current_user.full_name }}{% endif %}</p>
  </div>
  <a href="{{ url_for('web_books.catalog') }}" class="btn btn-gold">📚 کاتالوگ</a>
</div>

<!-- Stats cards -->
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:1rem; margin-bottom:2rem;">
  <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--teal-500);">
    <p style="color:var(--gray-500); font-size:.85rem;">کل کتاب‌ها</p>
    <p style="font-size:2rem; color:var(--navy-900); font-weight:700;">{{ stats.total_books }}</p>
  </div>
  <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--success);">
    <p style="color:var(--gray-500); font-size:.85rem;">موجود</p>
    <p style="font-size:2rem; color:var(--success); font-weight:700;">{{ stats.available_books }}</p>
  </div>
  <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--gold-500);">
    <p style="color:var(--gray-500); font-size:.85rem;">اعضا</p>
    <p style="font-size:2rem; color:var(--navy-900); font-weight:700;">{{ stats.total_users }}</p>
  </div>
  {% if current_user.is_authenticated and current_user.role in ('admin', 'employee') %}
    <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--warning);">
      <p style="color:var(--gray-500); font-size:.85rem;">درخواست‌های در انتظار</p>
      <p style="font-size:2rem; color:var(--warning); font-weight:700;">{{ stats.pending_requests }}</p>
    </div>
    <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--danger);">
      <p style="color:var(--gray-500); font-size:.85rem;">تأخیرها</p>
      <p style="font-size:2rem; color:var(--danger); font-weight:700;">{{ stats.overdue_loans }}</p>
    </div>
  {% endif %}
  {% if student_stats %}
    <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--teal-500);">
      <p style="color:var(--gray-500); font-size:.85rem;">امانت‌های فعال من</p>
      <p style="font-size:2rem; color:var(--navy-900); font-weight:700;">{{ student_stats.my_active }}</p>
    </div>
    <div style="background:#fff; padding:1.4rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06); border-right:4px solid var(--danger);">
      <p style="color:var(--gray-500); font-size:.85rem;">تأخیرهای من</p>
      <p style="font-size:2rem; color:var(--danger); font-weight:700;">{{ student_stats.my_overdue }}</p>
    </div>
  {% endif %}
</div>

<!-- Charts -->
<div style="display:grid; grid-template-columns:2fr 1fr; gap:1rem; margin-bottom:2rem;">
  <div style="background:#fff; padding:1.5rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06);">
    <h3 style="margin-bottom:1rem; color:var(--navy-900);">امانت‌های ۷ روز اخیر</h3>
    <canvas id="chart7d" height="100"></canvas>
  </div>
  <div style="background:#fff; padding:1.5rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06);">
    <h3 style="margin-bottom:1rem; color:var(--navy-900);">توزیع دسته‌ها</h3>
    <canvas id="chartCat" height="200"></canvas>
  </div>
</div>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:2rem;">
  <div style="background:#fff; padding:1.5rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06);">
    <h3 style="margin-bottom:1rem; color:var(--navy-900);">محبوب‌ترین کتاب‌ها</h3>
    {% if popular %}
      <ul style="list-style:none; padding:0;">
        {% for p in popular %}
          <li style="padding:.5rem 0; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between;">
            <span>{{ p.title }}</span>
            <span style="color:var(--gold-500); font-weight:600;">{{ p.count }} امانت</span>
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <p style="color:var(--gray-500);">هنوز داده‌ای نیست.</p>
    {% endif %}
  </div>

  {% if recent %}
    <div style="background:#fff; padding:1.5rem; border-radius:12px; box-shadow:0 4px 16px rgba(15,23,42,.06);">
      <h3 style="margin-bottom:1rem; color:var(--navy-900);">آخرین فعالیت‌ها</h3>
      <ul style="list-style:none; padding:0;">
        {% for r in recent %}
          <li style="padding:.5rem 0; border-bottom:1px solid #e2e8f0; font-size:.85rem;">
            <span style="color:var(--gold-500);">{{ r.action }}</span>
            {% if r.details %}<span style="color:var(--gray-500);">— {{ r.details }}</span>{% endif %}
            <span style="color:var(--gray-500); font-size:.75rem; display:block;">{{ r.created_at.strftime('%H:%M') }}</span>
          </li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}
</div>

<!-- Quick actions -->
<h2 style="font-size:1.3rem; margin-bottom:1rem; color:var(--navy-900);">دسترسی سریع</h2>
<div style="display:flex; gap:.8rem; flex-wrap:wrap;">
  <a href="{{ url_for('web_books.catalog') }}" class="btn btn-primary">📚 کاتالوگ</a>
  {% if current_user.is_authenticated %}
    {% if current_user.is_student %}
      <a href="{{ url_for('web_borrowings.my') }}" class="btn btn-gold">📖 امانت‌های من</a>
    {% endif %}
    {% if current_user.role in ('admin', 'employee') %}
      <a href="{{ url_for('web_borrowings.requests_list') }}" class="btn btn-gold">📋 درخواست‌ها</a>
      <a href="{{ url_for('web_borrowings.all_list') }}" class="btn btn-primary">📊 همه امانت‌ها</a>
      <a href="{{ url_for('web_books.manage') }}" class="btn" style="background:#e2e8f0; color:var(--navy-900);">⚙️ مدیریت</a>
    {% endif %}
    {% if current_user.is_admin %}
      <a href="{{ url_for('web_admin.audit_list') }}" class="btn" style="background:#e2e8f0; color:var(--navy-900);">📝 Audit</a>
    {% endif %}
  {% endif %}
</div>

<script>
  const cfg7d = {
    labels: {{ chart_7d.labels|tojson }},
    counts: {{ chart_7d.counts|tojson }}
  };
  new Chart(document.getElementById('chart7d'), {
    type: 'bar',
    data: {
      labels: cfg7d.labels,
      datasets: [{
        label: 'درخواست‌ها',
        data: cfg7d.counts,
        backgroundColor: 'rgba(20,184,166,0.7)',
        borderRadius: 6,
      }]
    },
    options: { responsive: true, plugins: { legend: { display: false } } }
  });

  const cfgCat = {
    labels: {{ chart_cat.labels|tojson }},
    counts: {{ chart_cat.counts|tojson }}
  };
  new Chart(document.getElementById('chartCat'), {
    type: 'doughnut',
    data: {
      labels: cfgCat.labels,
      datasets: [{
        data: cfgCat.counts,
        backgroundColor: ['#d4af37','#14b8a6','#3b82f6','#ef4444','#8b5cf6','#f59e0b','#10b981'],
      }]
    },
    options: { responsive: true }
  });
</script>
{% endblock %}
"""

FILES["app/templates/notifications/list.html"] = """{% extends 'base.html' %}
{% block title %}اعلان‌ها | MyLibrary{% endblock %}
{% block content %}
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
  <h1>اعلان‌ها</h1>
  {% if unread > 0 %}
    <form method="POST" action="{{ url_for('web_notifications.read_all') }}">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <button type="submit" class="btn btn-primary" style="padding:.5rem 1rem;">همه را خوانده کن</button>
    </form>
  {% endif %}
</div>

{% if items %}
  <div style="background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 16px rgba(15,23,42,.06);">
    {% for n in items %}
      <div style="padding:1rem 1.4rem; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; {% if not n.is_read %}background:#fef3c7;{% endif %}">
        <div>
          <h3 style="margin:0; color:var(--navy-900); font-size:1rem;">
            {% if not n.is_read %}<span style="color:var(--warning);">●</span>{% endif %}
            {{ n.title }}
          </h3>
          <p style="color:var(--gray-500); margin:.3rem 0; font-size:.9rem;">{{ n.message }}</p>
          <span style="color:var(--gray-500); font-size:.75rem;">{{ n.created_at.strftime('%Y-%m-%d %H:%M') }}</span>
        </div>
        {% if not n.is_read %}
          <form method="POST" action="{{ url_for('web_notifications.mark_read', nid=n.id) }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <button type="submit" class="btn" style="background:#e2e8f0; color:var(--navy-900); padding:.4rem .8rem; font-size:.8rem;">خوانده شد</button>
          </form>
        {% endif %}
      </div>
    {% endfor %}
  </div>
{% else %}
  <div style="background:#fff; padding:3rem; text-align:center; border-radius:12px; color:var(--gray-500);">
    اعلانی ندارید.
  </div>
{% endif %}
{% endblock %}
"""

FILES["app/templates/admin/audit.html"] = """{% extends 'base.html' %}
{% block title %}Audit Log | MyLibrary{% endblock %}
{% block content %}
<h1 style="margin-bottom:1.5rem;">Audit Log</h1>
<div style="background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 4px 16px rgba(15,23,42,.06);">
  <table style="width:100%; border-collapse:collapse; font-size:.85rem;">
    <thead style="background:var(--navy-900); color:#fff;">
      <tr>
        <th style="padding:.7rem; text-align:right;">تاریخ</th>
        <th style="padding:.7rem; text-align:right;">کاربر</th>
        <th style="padding:.7rem; text-align:right;">عملیات</th>
        <th style="padding:.7rem; text-align:right;">جزئیات</th>
        <th style="padding:.7rem; text-align:right;">IP</th>
      </tr>
    </thead>
    <tbody>
      {% for e in items %}
        <tr style="border-bottom:1px solid #e2e8f0;">
          <td style="padding:.5rem;">{{ e.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
          <td style="padding:.5rem;">{{ e.actor.email if e.actor else '—' }}</td>
          <td style="padding:.5rem;"><span style="color:var(--gold-500);">{{ e.action }}</span></td>
          <td style="padding:.5rem;">{{ e.details or '—' }}</td>
          <td style="padding:.5rem;">{{ e.ip_address or '—' }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
"""

FILES["app/templates/admin/audit_detail.html"] = """{% extends 'base.html' %}
{% block title %}Audit Detail | MyLibrary{% endblock %}
{% block content %}
<div class="card" style="max-width:720px; margin:0 auto;">
  <h1 class="card-title">جزئیات Audit</h1>
  <table style="width:100%;">
    <tr><td style="padding:.4rem; color:var(--gray-500);">ID:</td><td>{{ entry.id }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">Action:</td><td>{{ entry.action }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">User:</td><td>{{ entry.actor.email if entry.actor else '—' }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">Entity:</td><td>{{ entry.entity_type }} #{{ entry.entity_id }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">Details:</td><td>{{ entry.details or '—' }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">IP:</td><td>{{ entry.ip_address or '—' }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">UA:</td><td>{{ entry.user_agent or '—' }}</td></tr>
    <tr><td style="padding:.4rem; color:var(--gray-500);">تاریخ:</td><td>{{ entry.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</td></tr>
  </table>
  <a href="{{ url_for('web_admin.audit_list') }}" class="btn btn-primary" style="margin-top:1rem;">بازگشت</a>
</div>
{% endblock %}
"""

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path} ({len(content)} bytes)")

print("\nDONE: 4 UI templates written.")
