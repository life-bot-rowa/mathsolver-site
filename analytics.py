import os

GA_TAG = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-5DLHQQDXLW"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","G-5DLHQQDXLW");</script>"""

files = [
    "layouts/index.html",
    "layouts/price/single.html",
    "layouts/privacy-policy/single.html",
    "layouts/refund-policy/single.html",
    "layouts/terms-of-service/single.html",
    "layouts/access/single.html",
]

for path in files:
    if not os.path.exists(path):
        print(f"SKIP: {path}")
        continue
    content = open(path, encoding='utf-8').read()
    if 'G-5DLHQQDXLW' in content:
        print(f"- already has GA: {path}")
        continue
    content = content.replace('</head>', GA_TAG + '\n</head>', 1)
    open(path, 'w', encoding='utf-8').write(content)
    print(f"✓ {path}")

print("\n✅ Google Analytics добавлен!")
