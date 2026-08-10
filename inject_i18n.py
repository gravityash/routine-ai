import os

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add i18n.js
    if 'i18n.js' not in content:
        content = content.replace("<script src=\"{{ url_for('static', filename='theme.js') }}\"></script>", 
                                  "<script src=\"{{ url_for('static', filename='theme.js') }}\"></script>\n<script src=\"{{ url_for('static', filename='i18n.js') }}\"></script>")

    # Add language switcher
    lang_switcher = '<button class="lang-btn" data-lang="en" onclick="setLanguage(\'en\')" style="background:none; border:none; cursor:pointer; font-weight:800; color:inherit; text-decoration:underline;">EN</button><span style="margin:0 5px;">|</span><button class="lang-btn" data-lang="hi" onclick="setLanguage(\'hi\')" style="background:none; border:none; cursor:pointer; font-weight:600; color:inherit;">HI</button>'
    
    if 'lang-btn' not in content:
        if 'class="nav-links"' in content:
            content = content.replace('class="theme-toggle-btn" onclick="toggleTheme()" style="position:static; margin-right:15px; padding:0;">🌓</button>', 
                                      'class="theme-toggle-btn" onclick="toggleTheme()" style="position:static; margin-right:15px; padding:0;">🌓</button>\n            ' + lang_switcher)
        elif 'class="header"' in content and '<div style="position:absolute; top:0; right:0' in content:
            content = content.replace('<button onclick="toggleTheme()" style="background:none; border:none; padding:8px; box-shadow:none; cursor:pointer; font-size:1.5rem; margin:0; width:auto;">🌓</button>', 
                                      '<button onclick="toggleTheme()" style="background:none; border:none; padding:8px; box-shadow:none; cursor:pointer; font-size:1.5rem; margin:0; width:auto;">🌓</button>\n    ' + lang_switcher)
        elif '<button class="theme-toggle-btn"' in content:
            content = content.replace('<button class="theme-toggle-btn" onclick="toggleTheme()">🌓</button>',
                                      '<div style="position:absolute; top:20px; right:20px; display:flex; align-items:center; gap:10px;">\n        <button onclick="toggleTheme()" style="background:none; border:none; padding:8px; box-shadow:none; cursor:pointer; font-size:1.5rem; margin:0; width:auto;">🌓</button>\n        ' + lang_switcher + '\n    </div>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for f in os.listdir('templates'):
    if f.endswith('.html'):
        update_file(os.path.join('templates', f))

print("Injected i18n switcher to all templates.")
