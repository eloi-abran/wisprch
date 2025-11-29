# Maintainer: User <user@example.com>
pkgname=wisprch
pkgver=0.1.0
pkgrel=1
pkgdesc="A minimal, speech-to-text utility for Arch Linux"
arch=('any')
url="https://github.com/eloi-abran/wisprch"
license=('MIT')
depends=('python' 'python-sounddevice' 'python-openai' 'python-numpy' 'python-scipy' 'python-gobject' 'wl-clipboard' 'wtype')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("git+file://${PWD}")
sha256sums=('SKIP')

build() {
    cd "$pkgname"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname"
    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install systemd user service
    install -Dm644 systemd/wisprch.service "$pkgdir/usr/lib/systemd/user/wisprch.service"
    
    # Install default config (optional, maybe as example)
    install -Dm644 config/wisprch.conf "$pkgdir/usr/share/doc/$pkgname/wisprch.conf.example"
    
    # Install License
    install -Dm644 LICENCE.md "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
