import os

# 1. Update theme.css
with open('static/theme.css', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('body.dark-mode', 'html.dark-mode body')

with open('static/theme.css', 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Update home.html
with open('templates/home.html', 'r', encoding='utf-8') as f:
    home = f.read()
home = home.replace('style="list-style:none; padding:0; line-height:2.5; color:var(--text-gray); font-weight:600;"', 'class="text-gray" style="list-style:none; padding:0; line-height:2.5; font-weight:600;"')
home = home.replace('style="color:var(--text-gray); font-size:1.1rem;"', 'class="text-gray" style="font-size:1.1rem;"')
home = home.replace('style="text-align:left; font-size:0.9rem; color:var(--text-gray); padding-left:20px; line-height:1.6;"', 'class="text-gray" style="text-align:left; font-size:0.9rem; padding-left:20px; line-height:1.6;"')
home = home.replace('style="color:var(--text-gray); font-size:1.2rem; margin-bottom:30px;"', 'class="text-gray" style="font-size:1.2rem; margin-bottom:30px;"')

with open('templates/home.html', 'w', encoding='utf-8') as f:
    f.write(home)

# 3. Update dashboard.html
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    dashboard = f.read()

dashboard = dashboard.replace('style="margin-bottom: 20px; color: #475569;"', 'class="text-gray" style="margin-bottom: 20px;"')
dashboard = dashboard.replace('style="color:#475569; margin-bottom: 20px;"', 'class="text-gray" style="margin-bottom: 20px;"')
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard)

# 4. update hair_skin.html
with open('templates/hair_skin.html', 'r', encoding='utf-8') as f:
    hs = f.read()
hs = hs.replace('style="color: #475569;"', 'class="text-gray"')
hs = hs.replace('style="color: #94a3b8; font-size: 0.9em;"', 'class="text-gray" style="font-size: 0.9em;"')
with open('templates/hair_skin.html', 'w', encoding='utf-8') as f:
    f.write(hs)

print("Styles updated")
