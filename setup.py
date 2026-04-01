import os

# Все файлы создаются относительно текущей папки (mathsolver-site)


# ── ОБЩИЙ CSS И JS ──────────────────────────────────────────────────────────

CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --blue: #2B7FE8; --blue-dark: #1a5fc4; --yellow: #FFB800;
      --dark: #060D1F; --dark-2: #0D1B35; --dark-3: #112248;
      --white: #ffffff; --gray-text: #8a97b0; --text: #d4dff5;
      --radius: 16px; --radius-lg: 24px;
    }
    html { scroll-behavior: smooth; }
    body { font-family: 'DM Sans', sans-serif; background: var(--dark); color: var(--text); line-height: 1.6; overflow-x: hidden; }
    h1,h2,h3,h4 { font-family: 'Bricolage Grotesque', sans-serif; line-height: 1.15; }
    header { position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 0 40px; height: 72px; display: flex; align-items: center; justify-content: space-between; background: rgba(6,13,31,0.9); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(43,127,232,0.12); }
    .logo { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.3rem; font-weight: 800; color: var(--white); text-decoration: none; display: flex; align-items: center; gap: 10px; }
    .logo-icon { width: 34px; height: 34px; background: linear-gradient(135deg, var(--blue), var(--yellow)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    nav { display: flex; align-items: center; gap: 4px; }
    nav a { color: var(--gray-text); text-decoration: none; font-size: 0.875rem; padding: 8px 14px; border-radius: 8px; transition: color 0.2s, background 0.2s; white-space: nowrap; }
    nav a:hover, nav a.active { color: var(--white); background: rgba(255,255,255,0.06); }
    .btn-contact { margin-left: 12px; background: var(--yellow) !important; color: var(--dark) !important; font-weight: 600 !important; padding: 9px 20px !important; border-radius: 50px !important; transition: transform 0.2s !important; }
    .btn-contact:hover { transform: translateY(-1px) !important; }
    .hamburger { display: none; flex-direction: column; gap: 5px; cursor: pointer; padding: 4px; background: none; border: none; }
    .hamburger span { display: block; width: 24px; height: 2px; background: var(--white); border-radius: 2px; }
    .page-hero { padding: 140px 40px 80px; text-align: center; background: radial-gradient(ellipse 70% 50% at 50% 0%, rgba(43,127,232,0.18) 0%, transparent 70%), var(--dark); border-bottom: 1px solid rgba(43,127,232,0.1); }
    .section-label { display: inline-block; font-size: 0.75rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--blue); margin-bottom: 16px; }
    .page-hero h1 { font-size: clamp(2rem,5vw,3.5rem); font-weight: 800; color: var(--white); letter-spacing: -0.02em; margin-bottom: 16px; }
    .page-hero p { font-size: 1.05rem; color: var(--gray-text); font-weight: 300; }
    .container { max-width: 800px; margin: 0 auto; padding: 0 40px; }
    .content-wrap { padding: 80px 0; }
    .content-body h2 { font-size: 1.5rem; color: var(--white); margin: 40px 0 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(43,127,232,0.15); }
    .content-body p { font-size: 0.95rem; color: var(--text); line-height: 1.8; margin-bottom: 14px; font-weight: 300; }
    .content-body strong { color: var(--white); font-weight: 600; }
    .content-body ol { padding-left: 20px; margin-bottom: 14px; }
    .content-body li { font-size: 0.95rem; color: var(--text); line-height: 1.8; margin-bottom: 6px; font-weight: 300; }
    .content-body a { color: var(--blue); text-decoration: none; }
    .content-body a:hover { text-decoration: underline; }
    .price-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 24px; margin: 48px 0; }
    .price-card { background: var(--dark-2); border: 1px solid rgba(43,127,232,0.15); border-radius: var(--radius-lg); padding: 36px 28px; text-align: center; transition: border-color 0.2s, transform 0.2s; position: relative; }
    .price-card:hover { border-color: var(--blue); transform: translateY(-4px); }
    .price-card.featured { border-color: var(--blue); background: linear-gradient(135deg, rgba(43,127,232,0.12), var(--dark-2)); }
    .price-badge { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: var(--yellow); color: var(--dark); font-size: 0.7rem; font-weight: 700; padding: 4px 14px; border-radius: 50px; white-space: nowrap; }
    .price-period { font-size: 0.8rem; color: var(--gray-text); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }
    .price-amount { font-family: 'Bricolage Grotesque', sans-serif; font-size: 3rem; font-weight: 800; color: var(--white); line-height: 1; margin-bottom: 6px; }
    .price-amount span { font-size: 1.2rem; color: var(--gray-text); font-weight: 400; }
    .price-note { font-size: 0.8rem; color: var(--yellow); margin-bottom: 28px; min-height: 18px; }
    .price-btn { display: inline-block; background: var(--blue); color: var(--white); font-weight: 600; font-size: 0.9rem; padding: 12px 28px; border-radius: 50px; text-decoration: none; transition: background 0.2s; }
    .price-btn:hover { background: var(--blue-dark); }
    .price-card.featured .price-btn { background: var(--yellow); color: var(--dark); }
    footer { border-top: 1px solid rgba(255,255,255,0.06); padding: 48px 0 32px; }
    .footer-inner { display: flex; flex-direction: column; align-items: center; gap: 28px; max-width: 1160px; margin: 0 auto; padding: 0 40px; }
    .footer-logo { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.2rem; font-weight: 700; color: var(--white); text-decoration: none; }
    .footer-nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; }
    .footer-nav a { color: var(--gray-text); text-decoration: none; font-size: 0.875rem; padding: 6px 14px; border-radius: 8px; transition: color 0.2s; }
    .footer-nav a:hover { color: var(--white); }
    .footer-copy { text-align: center; color: rgba(255,255,255,0.25); font-size: 0.8rem; line-height: 1.8; }
    @media (max-width: 900px) {
      header { padding: 0 20px; }
      nav { display: none; }
      nav.open { display: flex; flex-direction: column; position: fixed; top: 72px; left: 0; right: 0; background: rgba(6,13,31,0.98); padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.08); gap: 4px; }
      nav.open a { padding: 12px 16px; font-size: 1rem; }
      nav.open .btn-contact { margin-left: 0; }
      .hamburger { display: flex; }
      .container { padding: 0 20px; }
      .page-hero { padding: 120px 20px 60px; }
      .price-grid { grid-template-columns: 1fr; max-width: 360px; margin: 48px auto; }
    }
"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Sans:opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500&display=swap" rel="stylesheet">'

JS = """
<script>
  const h = document.getElementById('hamburger');
  const n = document.getElementById('main-nav');
  if(h) h.addEventListener('click', () => n.classList.toggle('open'));
  document.addEventListener('click', e => { if(h && !h.contains(e.target) && !n.contains(e.target)) n.classList.remove('open'); });
  const obs = new IntersectionObserver(entries => entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); }), {threshold:0.15});
  document.querySelectorAll('.fade-up').forEach(el => obs.observe(el));
</script>
"""

PADDLE = """
<script src="https://cdn.paddle.com/paddle/v2/paddle.js"></script>
<script src="https://ai-math-solver-3a62b.web.app/checkout.js"></script>
"""

def header(active=""):
    links = [
        ("Home", "/", ""),
        ("Privacy notice", "/privacy-policy/", "privacy-policy"),
        ("Refund policy", "/refund-policy/", "refund-policy"),
        ("Price", "/price/", "price"),
        ("Terms of Service", "/terms-of-service/", "terms-of-service"),
    ]
    nav = ""
    for label, href, key in links:
        cls = ' class="active"' if key == active else ''
        nav += f'<a href="{href}"{cls}>{label}</a>\n      '
    nav += '<a href="/#contactus" class="btn-contact">Contact US</a>'
    return f"""
  <header>
    <a href="/" class="logo"><span class="logo-icon">&#8721;</span>MathSolver</a>
    <button class="hamburger" id="hamburger" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    <nav id="main-nav">{nav}</nav>
  </header>"""

def footer():
    return """
  <footer>
    <div class="footer-inner">
      <a href="/" class="footer-logo">MathSolver</a>
      <nav class="footer-nav">
        <a href="/">Home</a>
        <a href="/privacy-policy/">Privacy notice</a>
        <a href="/refund-policy/">Refund policy</a>
        <a href="/price/">Price</a>
        <a href="/terms-of-service/">Terms of Service</a>
      </nav>
      <div class="footer-copy">Copyright &copy; 2024 &ldquo;MARGOAPPS&rdquo; LLC<br>Armenia, Yervand Kochar Street, 8 &mdash; Yerevan, 0070</div>
    </div>
  </footer>"""

def wrap(title, desc, active, body, is_home=False):
    paddle = PADDLE if not False else ""  # всегда добавляем paddle на все страницы кроме блога
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} &mdash; MathSolver</title>
  <meta name="description" content="{desc}">
  {FONTS}
  <style>{CSS}</style>
</head>
<body>
{header(active)}
{body}
{footer()}
{PADDLE}
{JS}
</body>
</html>"""

# ── HOMEPAGE ────────────────────────────────────────────────────────────────

HOME_EXTRA_CSS = """
    body::before { content:''; position:fixed; inset:0; background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E"); pointer-events:none; z-index:0; opacity:0.6; }
    section { position:relative; z-index:1; }
    #hero { position:relative; min-height:100vh; display:flex; align-items:center; justify-content:center; text-align:center; padding:120px 40px 80px; overflow:hidden; }
    .hero-bg { position:absolute; inset:0; background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(43,127,232,0.22) 0%, transparent 70%), radial-gradient(ellipse 40% 40% at 80% 80%, rgba(255,184,0,0.08) 0%, transparent 60%), var(--dark); }
    .hero-grid { position:absolute; inset:0; background-image: linear-gradient(rgba(43,127,232,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(43,127,232,0.06) 1px, transparent 1px); background-size:60px 60px; mask-image:radial-gradient(ellipse at center, black 0%, transparent 70%); }
    .hero-content { position:relative; z-index:1; max-width:820px; }
    .hero-badge { display:inline-flex; align-items:center; gap:8px; background:rgba(43,127,232,0.15); border:1px solid rgba(43,127,232,0.3); color:#7eb8ff; font-size:0.8rem; font-weight:500; padding:6px 16px; border-radius:50px; margin-bottom:32px; letter-spacing:0.5px; text-transform:uppercase; }
    .hero-badge::before { content:''; width:6px; height:6px; border-radius:50%; background:var(--blue); animation:pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.4)} }
    h1.hero-title { font-size:clamp(2.4rem,6vw,5rem); font-weight:800; color:var(--white); margin-bottom:24px; letter-spacing:-0.02em; }
    h1.hero-title .accent { background:linear-gradient(135deg,var(--blue) 0%,#7eb8ff 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .hero-sub { font-size:clamp(1rem,2vw,1.2rem); color:var(--gray-text); max-width:560px; margin:0 auto 40px; line-height:1.7; font-weight:300; }
    .hero-cta { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }
    .btn-primary { display:inline-flex; align-items:center; gap:10px; background:var(--blue); color:var(--white); font-family:'DM Sans',sans-serif; font-weight:600; font-size:1rem; padding:15px 32px; border-radius:50px; text-decoration:none; transition:transform 0.2s,box-shadow 0.2s,background 0.2s; border:none; cursor:pointer; }
    .btn-primary:hover { background:var(--blue-dark); transform:translateY(-2px); box-shadow:0 8px 30px rgba(43,127,232,0.4); }
    .btn-secondary { display:inline-flex; align-items:center; gap:10px; background:transparent; color:var(--white); font-family:'DM Sans',sans-serif; font-weight:500; font-size:1rem; padding:15px 32px; border-radius:50px; text-decoration:none; border:1px solid rgba(255,255,255,0.2); transition:border-color 0.2s,background 0.2s; }
    .btn-secondary:hover { border-color:rgba(255,255,255,0.5); background:rgba(255,255,255,0.05); }
    .hero-scroll { position:absolute; bottom:40px; left:50%; transform:translateX(-50%); display:flex; flex-direction:column; align-items:center; gap:8px; color:var(--gray-text); font-size:0.75rem; letter-spacing:1px; text-transform:uppercase; animation:float 3s ease-in-out infinite; }
    .hero-scroll::after { content:''; width:1px; height:40px; background:linear-gradient(to bottom,var(--gray-text),transparent); }
    @keyframes float { 0%,100%{transform:translateX(-50%) translateY(0)} 50%{transform:translateX(-50%) translateY(8px)} }
    .section-divider { height:1px; background:linear-gradient(90deg,transparent,rgba(43,127,232,0.2),transparent); margin:0 40px; }
    .home-container { max-width:1160px; margin:0 auto; padding:0 40px; }
    .section-title { font-size:clamp(2rem,4vw,3rem); font-weight:800; color:var(--white); margin-bottom:20px; letter-spacing:-0.02em; }
    .section-sub { font-size:1.05rem; color:var(--gray-text); max-width:560px; line-height:1.7; font-weight:300; }
    #how-it-works { padding:120px 0; }
    #how-it-works .home-container { display:grid; grid-template-columns:1fr 1fr; gap:80px; align-items:center; }
    .steps-list { list-style:none; }
    .step-item { display:flex; gap:24px; padding:28px 0; border-bottom:1px solid rgba(255,255,255,0.06); }
    .step-item:last-child { border-bottom:none; }
    .step-num { flex-shrink:0; width:48px; height:48px; border-radius:12px; background:linear-gradient(135deg,rgba(43,127,232,0.2),rgba(43,127,232,0.05)); border:1px solid rgba(43,127,232,0.3); display:flex; align-items:center; justify-content:center; font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.1rem; color:var(--blue); }
    .step-body h3 { font-size:1.1rem; font-weight:700; color:var(--white); margin-bottom:8px; }
    .step-body p { font-size:0.9rem; color:var(--gray-text); line-height:1.65; font-weight:300; }
    .visual-card { background:var(--dark-2); border:1px solid rgba(43,127,232,0.15); border-radius:var(--radius-lg); padding:40px; position:relative; overflow:hidden; }
    .visual-card::before { content:''; position:absolute; top:-40px; right:-40px; width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(43,127,232,0.15),transparent 70%); }
    .visual-icon { font-size:4rem; margin-bottom:24px; display:block; }
    .visual-card h3 { font-size:1.4rem; color:var(--white); margin-bottom:12px; }
    .visual-card p { color:var(--gray-text); font-size:0.9rem; line-height:1.65; }
    .visual-tag { display:inline-flex; align-items:center; gap:6px; background:rgba(255,184,0,0.12); border:1px solid rgba(255,184,0,0.25); color:var(--yellow); font-size:0.75rem; font-weight:600; padding:5px 12px; border-radius:50px; margin-top:20px; }
    #about { padding:100px 0; background:linear-gradient(180deg,transparent,var(--dark-2) 20%,var(--dark-2) 80%,transparent); }
    #about .home-container { display:grid; grid-template-columns:1fr 1fr; gap:80px; align-items:center; }
    .about-stats { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:40px; }
    .stat-card { background:var(--dark-3); border:1px solid rgba(43,127,232,0.12); border-radius:var(--radius); padding:24px; }
    .stat-num { font-family:'Bricolage Grotesque',sans-serif; font-size:2.2rem; font-weight:800; color:var(--yellow); line-height:1; margin-bottom:6px; }
    .stat-label { font-size:0.8rem; color:var(--gray-text); font-weight:300; }
    .about-visual { background:var(--dark-3); border:1px solid rgba(43,127,232,0.15); border-radius:var(--radius-lg); padding:48px 40px; text-align:center; }
    .about-visual .big-icon { font-size:5rem; display:block; margin-bottom:24px; }
    .about-visual h3 { font-size:1.5rem; color:var(--white); margin-bottom:12px; }
    .about-visual p { color:var(--gray-text); font-size:0.9rem; font-weight:300; line-height:1.7; }
    #product { padding:120px 0; }
    .product-card { background:linear-gradient(135deg,var(--dark-2) 0%,var(--dark-3) 100%); border:1px solid rgba(43,127,232,0.2); border-radius:var(--radius-lg); padding:64px; display:grid; grid-template-columns:1fr auto; gap:60px; align-items:center; position:relative; overflow:hidden; }
    .product-card::before { content:''; position:absolute; top:0; right:0; width:400px; height:400px; background:radial-gradient(circle at top right,rgba(43,127,232,0.12),transparent 60%); }
    .product-text { position:relative; z-index:1; }
    .product-features { list-style:none; margin:28px 0 36px; display:flex; flex-direction:column; gap:12px; }
    .product-features li { display:flex; align-items:flex-start; gap:12px; font-size:0.9rem; color:var(--text); font-weight:300; }
    .product-features li::before { content:'✓'; flex-shrink:0; width:20px; height:20px; background:rgba(43,127,232,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; color:var(--blue); font-weight:700; margin-top:2px; }
    .product-img-card { width:280px; height:280px; background:linear-gradient(135deg,#1a3a6e,#0d2247); border-radius:var(--radius-lg); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; border:1px solid rgba(43,127,232,0.25); box-shadow:0 20px 60px rgba(0,0,0,0.4); position:relative; z-index:1; }
    .product-img-card .big-logo { font-size:4rem; }
    .product-img-card span { font-family:'Bricolage Grotesque',sans-serif; font-size:1.2rem; font-weight:700; color:var(--white); }
    .product-img-card small { font-size:0.75rem; color:var(--yellow); font-weight:500; }
    #contactus { padding:120px 0; background:linear-gradient(180deg,transparent,var(--dark-2) 30%,var(--dark-2) 70%,transparent); }
    #contactus .home-container { display:grid; grid-template-columns:1fr 1fr; gap:80px; align-items:start; }
    .contact-detail { display:flex; align-items:center; gap:14px; padding:16px 0; border-bottom:1px solid rgba(255,255,255,0.06); color:var(--text); text-decoration:none; font-size:0.9rem; transition:color 0.2s; }
    .contact-detail:hover { color:var(--blue); }
    .contact-detail:last-child { border-bottom:none; }
    .contact-icon { width:40px; height:40px; border-radius:10px; background:rgba(43,127,232,0.12); border:1px solid rgba(43,127,232,0.2); display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0; }
    .contact-form-wrap { background:var(--dark-3); border:1px solid rgba(43,127,232,0.15); border-radius:var(--radius-lg); padding:40px; }
    .form-row { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; }
    .form-group { display:flex; flex-direction:column; gap:8px; margin-bottom:16px; }
    .form-group label { font-size:0.8rem; font-weight:500; color:var(--gray-text); text-transform:uppercase; letter-spacing:0.5px; }
    .form-group input, .form-group textarea { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:14px 16px; font-family:'DM Sans',sans-serif; font-size:0.9rem; color:var(--white); outline:none; transition:border-color 0.2s,background 0.2s; width:100%; }
    .form-group input::placeholder, .form-group textarea::placeholder { color:rgba(255,255,255,0.2); }
    .form-group input:focus, .form-group textarea:focus { border-color:var(--blue); background:rgba(43,127,232,0.05); }
    .form-group textarea { resize:vertical; min-height:120px; }
    .form-submit { width:100%; background:var(--blue); color:var(--white); font-family:'DM Sans',sans-serif; font-weight:600; font-size:1rem; padding:15px 32px; border:none; border-radius:50px; cursor:pointer; transition:background 0.2s,transform 0.2s; }
    .form-submit:hover { background:var(--blue-dark); transform:translateY(-1px); }
    .form-msg { display:none; margin-top:16px; padding:14px 18px; border-radius:10px; font-size:0.875rem; text-align:center; }
    .form-msg.success { background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.25); color:#4ade80; }
    .form-msg.error { background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.25); color:#f87171; }
    .fade-up { opacity:0; transform:translateY(30px); transition:opacity 0.6s ease,transform 0.6s ease; }
    .fade-up.visible { opacity:1; transform:translateY(0); }
    @media (max-width:900px) {
      #hero { padding:100px 20px 80px; }
      #how-it-works .home-container, #about .home-container, #contactus .home-container { grid-template-columns:1fr; gap:48px; }
      .product-card { grid-template-columns:1fr; padding:40px 28px; }
      .product-img-card { display:none; }
      .about-stats { grid-template-columns:1fr 1fr; }
      .form-row { grid-template-columns:1fr; }
      .home-container { padding:0 20px; }
      #how-it-works, #product, #contactus { padding:80px 0; }
      #about { padding:80px 0; }
    }
    @media (max-width:560px) {
      .hero-cta { flex-direction:column; align-items:center; }
      .about-stats { grid-template-columns:1fr; }
      .contact-form-wrap { padding:28px 20px; }
    }
"""

HOME_BODY = """
  <section id="hero">
    <div class="hero-bg"></div>
    <div class="hero-grid"></div>
    <div class="hero-content">
      <div class="hero-badge">AI-Powered Math Solver</div>
      <h1 class="hero-title">Get Your Math Issues<br>Solved, <span class="accent">Fast and Easy</span></h1>
      <p class="hero-sub">An AI-powered tool designed to help you solve complex math problems with ease and accuracy — guiding you step by step like a personal tutor.</p>
      <div class="hero-cta">
        <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="btn-primary" target="_blank" rel="noopener">&#9889; Add to Chrome &mdash; Free</a>
        <a href="#how-it-works" class="btn-secondary">See how it works &darr;</a>
      </div>
    </div>
    <div class="hero-scroll">Scroll</div>
  </section>

  <div class="section-divider"></div>

  <section id="how-it-works">
    <div class="home-container">
      <div class="fade-up">
        <span class="section-label">How it works</span>
        <h2 class="section-title">Three steps to<br>your answer</h2>
        <p class="section-sub">No sign-up required. Works on any math problem right in your browser.</p>
        <ul class="steps-list" style="margin-top:40px">
          <li class="step-item"><div class="step-num">1</div><div class="step-body"><h3>Upload Your Issue / Task</h3><p>Simply upload your task or snap a quick screenshot. Whether it&rsquo;s algebra, calculus, or geometry &mdash; handwritten notes, typed equations, or textbook problems. No hassle, just upload.</p></div></li>
          <li class="step-item"><div class="step-num">2</div><div class="step-body"><h3>Get Answer from AI</h3><p>Our AI solver instantly analyzes your uploaded problem and delivers the correct solution in seconds &mdash; providing an accurate answer every time, saving you time and effort.</p></div></li>
          <li class="step-item"><div class="step-num">3</div><div class="step-body"><h3>Ask for Detailed Answer</h3><p>Request a detailed explanation to see the entire process, step by step. Perfect for students who want to learn, not just copy an answer.</p></div></li>
        </ul>
      </div>
      <div class="fade-up">
        <div class="visual-card">
          <span class="visual-icon">&#128208;</span>
          <h3>Solve any math problem instantly</h3>
          <p>From basic arithmetic to advanced calculus &mdash; algebra, geometry, trigonometry, statistics and more. Full step-by-step explanations included.</p>
          <div class="visual-tag">&#10022; Works directly in your browser</div>
        </div>
      </div>
    </div>
  </section>

  <div class="section-divider"></div>

  <section id="about">
    <div class="home-container">
      <div class="fade-up">
        <span class="section-label">About us</span>
        <h2 class="section-title">We build tools that<br>make you smarter</h2>
        <p class="section-sub">We create simple mobile applications and browser extensions that empower users to work smarter and increase productivity.</p>
        <div class="about-stats">
          <div class="stat-card"><div class="stat-num">2K+</div><div class="stat-label">Active users daily</div></div>
          <div class="stat-card"><div class="stat-num">4.8&#9733;</div><div class="stat-label">Chrome Store rating</div></div>
          <div class="stat-card"><div class="stat-num">100+</div><div class="stat-label">Math topic types</div></div>
          <div class="stat-card"><div class="stat-num">Free</div><div class="stat-label">Basic plan forever</div></div>
        </div>
      </div>
      <div class="about-visual fade-up">
        <span class="big-icon">&#127970;</span>
        <h3>&ldquo;MARGOAPPS&rdquo; LLC</h3>
        <p>We create simple, elegant tools that solve real problems. MathSolver is our flagship product &mdash; a Chrome extension that brings the power of AI math tutoring to any student or professional.</p>
      </div>
    </div>
  </section>

  <div class="section-divider"></div>

  <section id="product">
    <div class="home-container">
      <div class="product-card fade-up">
        <div class="product-text">
          <span class="section-label">Our product</span>
          <h2 class="section-title" style="font-size:clamp(1.8rem,3vw,2.6rem)">The MathSolver<br>Chrome Extension</h2>
          <ul class="product-features">
            <li>Upload your math task or snap a screenshot &mdash; AI instantly analyzes it</li>
            <li>Delivers precise solutions in seconds, handling complex equations</li>
            <li>Request step-by-step explanations to understand the full process</li>
            <li>Works directly in your browser &mdash; no app install needed</li>
            <li>Supports algebra, calculus, geometry, trigonometry, and more</li>
          </ul>
          <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="btn-primary" target="_blank" rel="noopener">&#128229; Download &mdash; It&rsquo;s Free</a>
        </div>
        <div class="product-img-card">
          <span class="big-logo">&#129518;</span>
          <span>MathSolver</span>
          <small>solve math with AI</small>
        </div>
      </div>
    </div>
  </section>

  <div class="section-divider"></div>

  <section id="contactus">
    <div class="home-container">
      <div class="contact-info fade-up">
        <span class="section-label">Contact us</span>
        <h2 class="section-title">Get in touch</h2>
        <p class="section-sub" style="margin-bottom:40px">Have a question or need support? Fill out the form and we&rsquo;ll get back to you shortly.</p>
        <a href="mailto:support@mathsolver.cloud" class="contact-detail"><span class="contact-icon">&#9993;</span>support@mathsolver.cloud</a>
        <div class="contact-detail"><span class="contact-icon">&#128205;</span>Armenia, Yervand Kochar Street, 8, Yerevan 0070</div>
        <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="contact-detail" target="_blank" rel="noopener"><span class="contact-icon">&#128279;</span>MathSolver on Chrome Web Store</a>
      </div>
      <div class="contact-form-wrap fade-up">
        <form id="contact-form" novalidate>
          <div class="form-row">
            <div class="form-group"><label for="first-name">First Name *</label><input type="text" id="first-name" name="first_name" placeholder="John" required></div>
            <div class="form-group"><label for="last-name">Last Name *</label><input type="text" id="last-name" name="last_name" placeholder="Doe" required></div>
          </div>
          <div class="form-group"><label for="email">Email *</label><input type="email" id="email" name="email" placeholder="example@mail.com" required></div>
          <div class="form-group"><label for="message">Message *</label><textarea id="message" name="message" placeholder="Enter your message" required></textarea></div>
          <button type="submit" class="form-submit">Send Message &rarr;</button>
          <div class="form-msg success" id="msg-success">&#10003; Thank you for your message. We will reply to you shortly!</div>
          <div class="form-msg error" id="msg-error">&#10007; There has been some error while submitting the form. Please verify all form fields again.</div>
        </form>
      </div>
    </div>
  </section>
<script>
  document.getElementById('contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const s = document.getElementById('msg-success');
    const er = document.getElementById('msg-error');
    s.style.display='none'; er.style.display='none';
    const d = Object.fromEntries(new FormData(this));
    if(!d.first_name||!d.last_name||!d.email||!d.message){er.style.display='block';return;}
    s.style.display='block'; this.reset();
  });
</script>
"""

def home_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Math Solver &mdash; Get Your Math Issues Solved, Fast and Easy!</title>
  <meta name="description" content="MathSolver is an AI-powered tool that solves complex math problems instantly. Take a screenshot, get a step-by-step solution in seconds.">
  {FONTS}
  <style>{CSS}{HOME_EXTRA_CSS}</style>
</head>
<body>
{header("")}
{HOME_BODY}
{footer()}
{PADDLE}
{JS}
</body>
</html>"""

# ── PRICE ───────────────────────────────────────────────────────────────────

PRICE_BODY = """
  <div class="page-hero">
    <span class="section-label">Pricing</span>
    <h1>Simple, Transparent Pricing</h1>
    <p>Start free, upgrade when you need more. No hidden fees.</p>
  </div>
  <div class="content-wrap">
    <div class="container" style="max-width:900px">
      <p style="text-align:center;color:var(--gray-text);font-weight:300">Our extension works on a subscription model. Choose the plan that suits you best.</p>
      <div class="price-grid">
        <div class="price-card">
          <div class="price-period">Weekly</div>
          <div class="price-amount">$2<span>.99<br><small style="font-size:.7rem">/ week</small></span></div>
          <div class="price-note">&#10022; 3 days free trial</div>
          <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="price-btn" target="_blank" rel="noopener">Get started</a>
        </div>
        <div class="price-card featured">
          <div class="price-badge">Most popular</div>
          <div class="price-period">Monthly</div>
          <div class="price-amount">$6<span>.99<br><small style="font-size:.7rem">/ month</small></span></div>
          <div class="price-note">&nbsp;</div>
          <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="price-btn" target="_blank" rel="noopener">Get started</a>
        </div>
        <div class="price-card">
          <div class="price-period">Yearly</div>
          <div class="price-amount">$19<span>.99<br><small style="font-size:.7rem">/ year</small></span></div>
          <div class="price-note">&#10022; Best value</div>
          <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" class="price-btn" target="_blank" rel="noopener">Get started</a>
        </div>
      </div>
      <p style="text-align:center;font-size:.85rem;color:var(--gray-text);font-weight:300">All plans include full access to the MathSolver Chrome extension.<br>Questions? <a href="mailto:support@mathsolver.cloud" style="color:var(--blue)">support@mathsolver.cloud</a></p>
    </div>
  </div>
"""

# ── PRIVACY ─────────────────────────────────────────────────────────────────

PRIVACY_BODY = """
  <div class="page-hero">
    <span class="section-label">Legal</span>
    <h1>Privacy Notice</h1>
    <p>How we collect, use, and protect your personal data.</p>
  </div>
  <div class="content-wrap"><div class="container"><div class="content-body">
    <h2>1. General Provisions</h2>
    <p>This personal data processing policy determines the procedure for processing personal data and measures to ensure the security of personal data undertaken by &ldquo;MARGOAPPS&rdquo; LLC (hereinafter referred to as the Operator).</p>
    <p>1.1. The Operator sets as its primary goal and condition for its activities the observance of the rights and freedoms of a person and citizen when processing their personal data, including the protection of the rights to privacy, personal and family secrets.</p>
    <p>1.2. This policy applies to all information that the Operator may receive about visitors to the website mathsolver.cloud</p>
    <h2>2. Key Concepts Used in the Policy</h2>
    <p>2.1. Automated processing of personal data &mdash; processing of personal data using computer technology.</p>
    <p>2.2. Blocking of personal data &mdash; temporary cessation of processing of personal data.</p>
    <p>2.3. Website &mdash; a set of graphic and informational materials ensuring their availability on the internet at the network address mathsolver.cloud</p>
    <p>2.4. Information system of personal data &mdash; a set of personal data contained in databases and information technologies and technical means ensuring their processing.</p>
    <p>2.5. Anonymization of personal data &mdash; actions resulting in the impossibility of determining the ownership of personal data to a specific User.</p>
    <p>2.6. Processing of personal data &mdash; any action or a set of actions performed with personal data, including collection, recording, systematization, accumulation, storage, clarification, extraction, use, transfer, anonymization, blocking, deletion, destruction of personal data.</p>
    <p>2.7. Operator &mdash; a legal entity that independently or jointly with other persons organizes and/or performs the processing of personal data.</p>
    <p>2.8. Personal data &mdash; any information relating directly or indirectly to a specific or identifiable User of the website mathsolver.cloud</p>
    <p>2.9. Personal data allowed for distribution &mdash; personal data to which an unlimited number of persons have been granted access by the subject of personal data.</p>
    <p>2.10. User &mdash; any visitor to the website mathsolver.cloud</p>
    <p>2.11. Provision of personal data &mdash; actions aimed at disclosing personal data to a specific person or a specific circle of persons.</p>
    <p>2.12. Distribution of personal data &mdash; any actions aimed at disclosing personal data to an indefinite circle of persons.</p>
    <p>2.13. Cross-border transfer of personal data &mdash; transfer of personal data to the territory of a foreign state.</p>
    <p>2.14. Destruction of personal data &mdash; any actions resulting in the irreversible destruction of personal data.</p>
    <h2>3. Basic Rights and Obligations of the Operator</h2>
    <p>3.1. The Operator has the right to receive reliable information from the subject of personal data; continue processing personal data without consent if there are grounds specified in the Personal Data Law; independently determine necessary measures to ensure fulfillment of obligations.</p>
    <p>3.2. The Operator is obliged to provide information regarding the processing of personal data upon request; organize processing in accordance with current legislation; respond to inquiries from subjects of personal data; take measures to protect personal data from unlawful access; fulfill other obligations provided for by the Personal Data Law.</p>
    <h2>4. Basic Rights and Obligations of Personal Data Subjects</h2>
    <p>4.1. Personal data subjects have the right to receive information regarding processing of their personal data; demand clarification, blocking or destruction of inaccurate data; withdraw consent to processing; appeal unlawful actions of the Operator in court.</p>
    <p>4.2. Personal data subjects are obliged to provide the Operator with reliable data about themselves and inform the Operator about any changes.</p>
    <p>4.3. Persons who provided false information bear responsibility in accordance with current legislation.</p>
    <h2>5. Principles of Personal Data Processing</h2>
    <p>5.1. Processing is carried out on a lawful and fair basis.</p>
    <p>5.2. Processing is limited to achieving specific, pre-defined, and lawful goals.</p>
    <p>5.3. It is not allowed to combine databases containing personal data for incompatible purposes.</p>
    <p>5.4. Only personal data that meet the purposes of processing are subject to processing.</p>
    <p>5.5. The content and volume of processed data correspond to the stated purposes.</p>
    <p>5.6. Accuracy of personal data is ensured during processing.</p>
    <p>5.7. Personal data is stored no longer than required by the purposes of processing.</p>
    <h2>6. Purposes of Personal Data Processing</h2>
    <p>The purpose of processing &mdash; informing the User by sending emails. Personal data: last name, first name, email address, phone numbers, city. Types of personal data processing: collection, recording, systematization, accumulation, storage, destruction, and anonymization of personal data.</p>
    <h2>7. Conditions for Personal Data Processing</h2>
    <p>7.1. Processing is carried out with the consent of the subject of personal data.</p>
    <p>7.2&ndash;7.7. Processing may also be carried out to achieve goals provided for by international treaty or law, for the administration of justice, for the execution of a contract, to exercise the rights and legitimate interests of the operator, for publicly available personal data, or for personal data subject to mandatory disclosure in accordance with federal law.</p>
    <h2>8. Procedure for Collecting, Storing, Transferring, and Other Types of Personal Data Processing</h2>
    <p>8.1. The Operator ensures the safety of personal data and takes all possible measures to exclude access by unauthorized persons.</p>
    <p>8.2. The User&rsquo;s personal data will never be transferred to third parties, except in cases related to the execution of current legislation or with the User&rsquo;s consent.</p>
    <p>8.3. In case of inaccuracies, the User can update their personal data by sending a notification to <a href="mailto:support@mathsolver.cloud">support@mathsolver.cloud</a> marked &ldquo;Updating personal data.&rdquo;</p>
    <p>8.4. The User can withdraw consent to processing at any time by sending a notification to <a href="mailto:support@mathsolver.cloud">support@mathsolver.cloud</a> marked &ldquo;Withdrawal of consent to personal data processing.&rdquo;</p>
    <p>8.5. All information collected by third-party services is stored and processed by those persons in accordance with their own User Agreement and Privacy Policy. The Operator is not responsible for the actions of third parties.</p>
    <p>8.6. Prohibitions established by the subject of personal data on transfer of personal data do not apply in cases of processing in state, public, and other public interests defined by law.</p>
  </div></div></div>
"""

# ── REFUND ──────────────────────────────────────────────────────────────────

REFUND_BODY = """
  <div class="page-hero">
    <span class="section-label">Legal</span>
    <h1>Refund Policy</h1>
    <p>We stand behind our product with a 20-day money-back guarantee.</p>
  </div>
  <div class="content-wrap"><div class="container"><div class="content-body">
    <p>Your satisfaction is our priority. We offer a <strong>20-day money-back guarantee</strong> on all digital products purchased through our website. If for any reason you are not completely satisfied with your digital purchase, you may request a full refund within 20 days of the purchase date &mdash; no questions asked.</p>
    <h2>How to Request a Refund</h2>
    <ol>
      <li><strong>Contact Us:</strong> Initiate your refund by contacting our customer support team at <a href="mailto:support@mathsolver.cloud">support@mathsolver.cloud</a>. Please include your order number and, optionally, the reason for requesting a refund, though you are not required to provide one.</li>
      <li><strong>Processing Your Refund:</strong> Once we receive your refund request, we will process it in 7 days. The refund will be credited back to the original method of payment. Please note that the timing of the refund appearing on your statement can vary based on the policies of the payment provider.</li>
    </ol>
    <p>We are committed to ensuring that our customers have a positive experience. If you have any questions or require assistance, please contact our support team at <a href="mailto:support@mathsolver.cloud">support@mathsolver.cloud</a></p>
  </div></div></div>
"""

# ── TERMS ───────────────────────────────────────────────────────────────────

TERMS_BODY = """
  <div class="page-hero">
    <span class="section-label">Legal</span>
    <h1>Terms of Service</h1>
    <p>Please read these terms carefully before using our services.</p>
  </div>
  <div class="content-wrap"><div class="container"><div class="content-body">
    <p>This agreement is an official offer (public offer) and contains all the essential conditions for the provision of services. In the event of acceptance of the terms set forth below and payment for services, the legal or physical entity accepting this offer becomes the Customer, and the Contractor (&ldquo;MARGOAPPS&rdquo; LLC) and the Customer collectively become the Parties to this agreement. If you do not agree with any clause of the offer, the Contractor suggests that you refrain from using the services.</p>
    <h2>1. General Terms</h2>
    <p>1.1. Acceptance of the offer &mdash; full and unconditional acceptance of the offer by the Customer&rsquo;s actions as specified in clause 3.4 of this offer.</p>
    <p>1.2. Customer &mdash; the entity that has accepted the offer and thus becomes the Customer of the Contractor&rsquo;s services.</p>
    <p>1.3. Contractor &mdash; Administration of the website mathsolver.cloud</p>
    <p>1.4. Offer Agreement &mdash; an agreement between the Contractor and the Customer for the provision of services, concluded by acceptance of the offer.</p>
    <p>1.5. Price List &mdash; the current systematic list of the Contractor&rsquo;s services with prices, published on the internet resource at: mathsolver.cloud</p>
    <h2>2. Subject of the Agreement</h2>
    <p>2.1. The subject of this offer is the provision of services to the Customer in accordance with the terms of this offer and the current price list.</p>
    <p>2.2. The Contractor has the right to unilaterally change the Price List and the terms of this public offer at any time, ensuring that updated terms are published at least three days before they come into effect.</p>
    <h2>3. Procedure for the Provision and Payment of Services</h2>
    <p>3.1. Services are provided in full subject to 100% payment by the Customer.</p>
    <p>3.2. After familiarizing themselves with the price list and the text of this offer, the Customer forms an electronic application on the website.</p>
    <p>3.3. Based on the received application, the Contractor issues an invoice for the selected service in electronic form.</p>
    <p>3.4. The Customer transfers funds to the Contractor&rsquo;s settlement account online through the payment system on the website.</p>
    <p>3.5. The offer agreement comes into force after the Customer&rsquo;s payment and the funds are credited to the Contractor&rsquo;s settlement account.</p>
    <p>3.6. From the moment of acceptance of the offer, the Contractor ensures the provision of services to the Customer.</p>
    <h2>4. Rights and Obligations of the Parties, Liability</h2>
    <p>4.1. The Contractor makes every effort to ensure the quality and uninterrupted provision of services.</p>
    <p>4.2. The Customer gains access to all tools specified in the service offer.</p>
    <p>4.3. The Customer is not entitled to copy and/or distribute the website materials in any way. In case of illegal actions, the Contractor has the right to deny the Customer further access and hold them liable in accordance with the law.</p>
    <p>4.4. The Contractor is not responsible for violating the terms of the agreement if such violation is caused by force majeure circumstances, including: actions of government authorities, fire, flood, earthquake, other natural disasters, power outages, strikes, civil unrest, or any other circumstances beyond the Contractor&rsquo;s control.</p>
    <p>4.5. In the event of inability to provide services due to the Contractor&rsquo;s fault, the Contractor undertakes to refund the payments made by the Customer. In other cases, refunds are not provided.</p>
    <p>4.6. For non-performance or improper performance of obligations, the Parties bear responsibility in accordance with current legislation.</p>
    <h2>5. Final Provisions</h2>
    <p>5.1. The agreement comes into force from the moment of acceptance of the offer and remains in effect until the Parties fulfill their obligations.</p>
    <p>5.2. In case of disputes, the Contractor and the Customer will take all measures to resolve them through negotiations. The claim review period is 15 (fifteen) business days.</p>
    <p>5.3. If it is impossible to resolve disputes through negotiations, such disputes shall be considered in accordance with the current legislation.</p>
    <p>5.4. Promo code discounts cannot be combined with other discounts and special offers.</p>
  </div></div></div>
"""

# ── ACCESS ──────────────────────────────────────────────────────────────────

ACCESS_BODY = """
  <div class="page-hero">
    <span class="section-label">Access</span>
    <h1>Math Solver Access</h1>
    <p>Manage your subscription and access your account.</p>
  </div>
  <div class="content-wrap">
    <div class="container" style="text-align:center;padding-top:20px">
      <p style="color:var(--gray-text);font-weight:300;margin-bottom:40px">To access MathSolver, install the Chrome extension from the Web Store.</p>
      <a href="https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb" style="display:inline-flex;align-items:center;gap:10px;background:var(--blue);color:var(--white);font-weight:600;font-size:1rem;padding:15px 32px;border-radius:50px;text-decoration:none" target="_blank" rel="noopener">&#128229; Open in Chrome Web Store</a>
    </div>
  </div>
"""

# ── WRITE FILES ─────────────────────────────────────────────────────────────

files = {
    "layouts/index.html": home_page(),
    "layouts/_default/baseof.html": "{{ block \"main\" . }}{{ end }}",
    "content/_index.md": "---\ntitle: Home\n---\n",
    "content/price.md": "---\ntitle: Price\nlayout: price\n---\n",
    "content/privacy-policy.md": "---\ntitle: Privacy Notice\nlayout: privacy-policy\n---\n",
    "content/refund-policy.md": "---\ntitle: Refund Policy\nlayout: refund-policy\n---\n",
    "content/terms-of-service.md": "---\ntitle: Terms of Service\nlayout: terms-of-service\n---\n",
    "content/access.md": "---\ntitle: Access\nlayout: access\n---\n",
    "layouts/price/single.html": wrap("Price", "Simple pricing for MathSolver.", "price", PRICE_BODY),
    "layouts/privacy-policy/single.html": wrap("Privacy Notice", "MathSolver privacy policy.", "privacy-policy", PRIVACY_BODY),
    "layouts/refund-policy/single.html": wrap("Refund Policy", "20-day money-back guarantee.", "refund-policy", REFUND_BODY),
    "layouts/terms-of-service/single.html": wrap("Terms of Service", "Terms and conditions for MathSolver.", "terms-of-service", TERMS_BODY),
    "layouts/access/single.html": wrap("Access", "Access your MathSolver account.", "access", ACCESS_BODY),
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ {path}")

print("\n✅ Готово! Все файлы созданы.")
print("Теперь запусти: hugo server")
