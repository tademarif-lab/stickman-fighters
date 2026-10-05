[app]
title = STICKMAN FIGHTERS
package.name = stickmanfighters
package.domain = com.katil5019
source.dir = app
source.include_exts = py,png,json,txt,jpg
source.exclude_dirs = __pycache__,.buildozer
version = 1.4.0

requirements = python3,pygame,setuptools

icon.filename = %(source.dir)s/oyun_ikon.png
presplash.filename = %(source.dir)s/kapak.png

orientation = landscape
fullscreen = 1

android.permissions = INTERNET
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.skip_update = False

p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0