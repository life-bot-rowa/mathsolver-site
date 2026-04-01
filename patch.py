# Патч для setup.py — добавляем EmailJS и UTM метки
# Запускать из папки mathsolver-site

SERVICE_ID = "service_7cbqshk"
TEMPLATE_ID = "template_ly83ru4"
PUBLIC_KEY = "p9euamwu53cviruiX8DVx"
CWS_URL = "https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb?utm_source=mathsolver.cloud&utm_medium=website&utm_campaign=main_site"

import os, re

files_to_patch = [
    "layouts/index.html",
    "layouts/price/single.html",
    "layouts/privacy-policy/single.html",
    "layouts/refund-policy/single.html",
    "layouts/terms-of-service/single.html",
    "layouts/access/single.html",
]

OLD_CWS = "https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb"

EMAILJS_SCRIPT = f"""<script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
<script>
  emailjs.init("{PUBLIC_KEY}");
</script>"""

OLD_FORM_JS = """<script>
  document.getElementById('contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const s = document.getElementById('msg-success');
    const er = document.getElementById('msg-error');
    s.style.display='none'; er.style.display='none';
    const d = Object.fromEntries(new FormData(this));
    if(!d.first_name||!d.last_name||!d.email||!d.message){er.style.display='block';return;}
    s.style.display='block'; this.reset();
  });
</script>"""

NEW_FORM_JS = f"""<script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
<script>
  emailjs.init("{PUBLIC_KEY}");
  document.getElementById('contact-form').addEventListener('submit', function(e) {{
    e.preventDefault();
    const btn = this.querySelector('.form-submit');
    const s = document.getElementById('msg-success');
    const er = document.getElementById('msg-error');
    s.style.display='none'; er.style.display='none';
    const d = Object.fromEntries(new FormData(this));
    if(!d.first_name||!d.last_name||!d.email||!d.message){{er.style.display='block';return;}}
    btn.textContent='Sending...'; btn.disabled=true;
    emailjs.send("{SERVICE_ID}", "{TEMPLATE_ID}", {{
      from_name: d.first_name + ' ' + d.last_name,
      email: d.email,
      message: d.message
    }}).then(() => {{
      s.style.display='block';
      this.reset();
      btn.textContent='Send Message \u2192';
      btn.disabled=false;
    }}, () => {{
      er.style.display='block';
      btn.textContent='Send Message \u2192';
      btn.disabled=false;
    }});
  }});
</script>"""

patched = 0
for path in files_to_patch:
    if not os.path.exists(path):
        print(f"SKIP (not found): {path}")
        continue
    content = open(path, encoding='utf-8').read()
    original = content

    # Replace CWS links with UTM
    content = content.replace(OLD_CWS, CWS_URL)

    # Replace form JS (only in index.html)
    if path == "layouts/index.html":
        content = content.replace(OLD_FORM_JS, NEW_FORM_JS)

    if content != original:
        open(path, 'w', encoding='utf-8').write(content)
        patched += 1
        print(f"✓ patched: {path}")
    else:
        print(f"- unchanged: {path}")

print(f"\n✅ Готово! Обновлено файлов: {patched}")
print("Теперь запусти: hugo server")
