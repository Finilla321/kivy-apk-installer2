[app]
title = Universal Installer
package.name = apkinstaller
package.domain = org.custom.installer
source.dir = .
source.include_exts = py,png,json
version = 1.0

# Требования для Kivy
requirements = python3,kivy

# Разрешения для работы с памятью и Shizuku
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, INTERNET

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.api = 34
android.minapi = 26
