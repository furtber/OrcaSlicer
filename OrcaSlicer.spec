Name:           OrcaSlicer
Version:        2.3.2
Release:        %autorelease
Summary:        OrcaSlicer is a tool for slicing 3D models for 3D printing.

License:        GNU AFFERO GENERAL PUBLIC LICENSE
Source0:        OrcaSlicer-%{version}.tar.gz

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  cmake
BuildRequires:  dbus-devel
BuildRequires:  eglexternalplatform-devel
BuildRequires:  extra-cmake-modules
BuildRequires:  file
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamermm-devel
BuildRequires:  gtk3-devel
BuildRequires:  libmspack-devel
BuildRequires:  libquadmath-devel
BuildRequires:  libsecret-devel
BuildRequires:  libspnav-devel
BuildRequires:  libtool
BuildRequires:  m4
BuildRequires:  mesa-libGLU-devel
BuildRequires:  ninja-build
BuildRequires:  openssl-devel
BuildRequires:  perl-FindBin
BuildRequires:  texinfo
BuildRequires:  wayland-protocols-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  wget
BuildRequires:  libcurl-devel
BuildRequires:  procps-ng
BuildRequires:  patchelf

%global install_dir /opt/OrcaSlicer

%description
OrcaSlicer is a powerful and user-friendly slicing software designed for 3D printing enthusiasts. It provides advanced features and a streamlined interface to help users prepare their 3D models for printing with precision and ease. With support for a wide range of 3D printers and materials, OrcaSlicer is the go-to choice for both beginners and experienced makers in the 3D printing community.

%prep
%setup

%build
rm -rf build
rm -rf deps/build
export CXXFLAGS="${CXXFLAGS} -std=c++17 -Wno-error=deprecated-declarations"
export CFLAGS="${CFLAGS} -Wno-error=deprecated-declarations"
./build_linux.sh -s -d -r

%install
# Application binary
install -d %{buildroot}%{install_dir}/bin
cp -a build/package/bin/. %{buildroot}%{install_dir}/bin/
# Fix build-time RPATHs: replace with $ORIGIN so co-located libs are found
# without relying on absolute build-machine paths (which rpmbuild rejects).
for f in %{buildroot}%{install_dir}/bin/*; do
    if file "$f" | grep -q ELF; then
        patchelf --set-rpath '$ORIGIN' "$f"
    fi
done

# Resources
install -d %{buildroot}%{install_dir}/resources
cp -a build/package/resources/. %{buildroot}%{install_dir}/resources/
# Launcher wrapper (uses fixed install path unlike the AppImage wrapper)
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/orca-slicer << 'EOF'
#!/bin/bash
ORCA_DIR=%{install_dir}
export LD_LIBRARY_PATH="$ORCA_DIR/bin:$LD_LIBRARY_PATH"
# OrcaSlicer segfault workaround: ensure locale info is set
export LC_ALL=C
if [ "$XDG_SESSION_TYPE" = "wayland" ] && [ "$ZINK_DISABLE_OVERRIDE" != "1" ]; then
    if command -v glxinfo >/dev/null 2>&1; then
        RENDERER=$(glxinfo | grep "OpenGL renderer string:" | sed 's/.*: //')
        if echo "$RENDERER" | grep -qi "NVIDIA"; then
            if command -v nvidia-smi >/dev/null 2>&1; then
                DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)
                DRIVER_MAJOR=$(echo "$DRIVER_VERSION" | cut -d. -f1)
                [ "$DRIVER_MAJOR" -gt 555 ] && ZINK_FORCE_OVERRIDE=1
            fi
            if [ "$ZINK_FORCE_OVERRIDE" = "1" ]; then
                export __GLX_VENDOR_LIBRARY_NAME=mesa
                export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json
                export MESA_LOADER_DRIVER_OVERRIDE=zink
                export GALLIUM_DRIVER=zink
                export WEBKIT_DISABLE_DMABUF_RENDERER=1
            fi
        fi
    fi
fi
exec "$ORCA_DIR/bin/orca-slicer" "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/orca-slicer

# Desktop entry
install -Dm644 src/dev-utils/platform/unix/com.orcaslicer.OrcaSlicer.desktop \
    %{buildroot}%{_datadir}/applications/com.orcaslicer.OrcaSlicer.desktop
# Icons (multiple sizes)
install -Dm644 resources/images/OrcaSlicer_192px.png \
    %{buildroot}%{_datadir}/icons/hicolor/192x192/apps/OrcaSlicer.png
install -Dm644 resources/images/OrcaSlicer_128px.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/OrcaSlicer.png
install -Dm644 resources/images/OrcaSlicer_64.png \
    %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/OrcaSlicer.png
install -Dm644 resources/images/OrcaSlicer_32px.png \
    %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/OrcaSlicer.png
%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/usr/bin/update-desktop-database &>/dev/null || :
%postun
if [ $1 -eq 0 ]; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &>/dev/null || :
%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%{_bindir}/orca-slicer
%{install_dir}/
%{_datadir}/applications/com.orcaslicer.OrcaSlicer.desktop
%{_datadir}/icons/hicolor/192x192/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/128x128/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/64x64/apps/OrcaSlicer.png
%{_datadir}/icons/hicolor/32x32/apps/OrcaSlicer.png


%changelog
%autochangelog
