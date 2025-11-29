# Maintainer: Eloi Abran <abran.labs@gmail.com>
pkgname=wisprch
pkgver=0.1.0
pkgrel=1
pkgdesc="A minimal, speech-to-text utility for Arch Linux"
arch=('any')
url="https://github.com/eloi-abran/wisprch"
license=('MIT')
depends=('python' 'python-openai' 'python-numpy' 'python-scipy' 'python-gobject' 'wl-clipboard' 'wtype' 'portaudio') # python-sounddevice is in AUR, portaudio is the system dep
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("repo_source::git+file://${PWD}")
sha256sums=('SKIP')

build() {
    cd "repo_source"
    /usr/bin/python -m build --wheel --no-isolation
}

package() {
    cd "repo_source"
    /usr/bin/python -m installer --destdir="$pkgdir" dist/*.whl

    # Install systemd user service
    install -Dm644 systemd/wisprch.service "$pkgdir/usr/lib/systemd/user/wisprch.service"
    
    # Install License
    install -Dm644 LICENCE.md "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
