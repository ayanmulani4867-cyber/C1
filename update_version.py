p = r'C:\Users\ayanm\AndroidStudioProjects\CampusConnectStudent\app\build.gradle.kts'
with open(p, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('versionCode = 2', 'versionCode = 3')
content = content.replace('versionName = "1.1.0"', 'versionName = "2.0.0"')

with open(p, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated build.gradle.kts successfully!")
