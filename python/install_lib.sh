#!/bin/bash
pip3 install -r requirements.txt

sudo yum install -y gconf-service \
    alsa-lib \
    atk \
    at-spi2-atk \
    glibc \
    cairo \
    cups-libs \
    dbus-libs \
    expat \
    fontconfig \
    libgcc \
    gdk-pixbuf2 \
    glib2 \
    gtk3 \
    nspr \
    pango \
    pangox-compat \
    libstdc++ \
    libX11 \
    libX11-xcb \
    libxcb \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXfixes \
    libXi \
    libXrandr \
    libXrender \
    libXScrnSaver \
    libXtst \
    ca-certificates \
    liberation-fonts-common liberation-mono-fonts liberation-narrow-fonts liberation-sans-fonts liberation-serif-fonts\
    libappindicator-gtk3 \
    nss-util nss-softokn nss-softokn-freebl nss-sysinit nss-tools nss nss-devel\
    redhat-lsb-core redhat-lsb-submod-security redhat-lsb-cxx redhat-lsb-desktop redhat-lsb-languages redhat-lsb-printing redhat-lsb-web\
    xdg-utils  \
    wget  \
    cairo-gobject-devel cairo-devel cairo-tools\
    xorg-x11-server-utils xorg-x11-server-Xorg xorg-x11-server-common xorg-x11-server-source xorg-x11-server-devel\
    gtk2-devel gtk2-immodules gtk2-immodule-xim gtk2-engines gtk2\
    pango-devel pangomm pangox-compat-devel pangox-compat\
    thai-scalable-waree-fonts thai-scalable-norasi-fonts thai-scalable-purisa-fonts thai-scalable-loma-fonts thai-scalable-garuda-fonts thai-scalable-kinnari-fonts thai-scalable-umpush-fonts thai-scalable-tlwgmono-fonts thai-scalable-tlwgtypist-fonts thai-scalable-tlwgtypewriter-fonts thai-scalable-tlwgmono-light-fonts thai-scalable-tlwgtypo-fonts\
    pixman pixman-devel pixman-tests\
    xcb-util-renderutil xcb-util-renderutil-devel\
    harfbuzz harfbuzz-devel harfbuzz-icu harfbuzz-doc\
    datrie datrie-devel\
    graphite2 graphite2-devel graphite2-doc\
    mesa-libgbm mesa-libgbm-devel
