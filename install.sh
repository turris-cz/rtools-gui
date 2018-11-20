#!/bin/sh
set -e
rtools_root="$(dirname "$(readlink -f "$0")")"

make -C mox-imager -j"$(nproc)"

virtualenv --system-site-packages -p python3 ~/.rtools-gui-env
. ~/.rtools-gui-env/bin/activate

pip install -r requirements.txt --upgrade

# If there is no desktop then skip (just to be nice)
[ -d ~/Desktop ] || exit 0
cat > ~/Desktop/Turris.desktop <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Turris MOX
GenericName=Programátor
TryExec=$rtools_root/rtools-gui.py
Exec=$(which python3) $rtools_root/rtools-gui.py
Terminal=false
StartupNotify=true
EOF
chmod +x ~/Desktop/Turris.desktop
