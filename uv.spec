#
# Conditional build:
%bcond_with	tests		# run cargo tests (most need network access)
#
%define		crates_ver	%{version}

# 32-bit linkers can't fit uv's debug info into the ~3 GB process
# address space, so drop debuginfo and the -debuginfo/-debugsource
# subpackages on 32-bit only.
%ifarch %{ix86} %{arm}
%define		_enable_debug_packages	0
%endif

Summary:	An extremely fast Python package and project manager
Summary(pl.UTF-8):	Bardzo szybki menedżer pakietów i projektów Pythonowych
Name:		uv
Version:	0.11.8
Release:	1
License:	MIT or Apache v2.0
Group:		Development/Tools
Source0:	https://github.com/astral-sh/uv/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	46ce221920634b509c17c1bd6373b49d
# poldek -uvg cargo-vendor-filterer
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2
# tar cJf uv-crates-%%{version}.tar.xz vendor Cargo.lock
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	2ff89da4d7c0cdb37b70d94652dd815d
Patch0:		lto.patch
URL:		https://github.com/astral-sh/uv
BuildRequires:	bzip2-devel
BuildRequires:	cargo
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.050
BuildRequires:	rust >= 1.93
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel
%{?rust_req}
ExclusiveArch:	%{rust_arches}
# aws-lc-sys (uv's TLS backend via aws-lc-rs) does not support x32:
# multiple inline-asm and 64-bit-limb paths gate on OPENSSL_X86_64
# alone, treating it as synonymous with 64-bit BN_ULONG, which breaks
# under x32's 32-bit pointers. aws-lc upstream lists no x32 target.
ExcludeArch:	x32
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
uv is an extremely fast Python package and project manager, written in
Rust. It is a drop-in replacement for pip, pip-tools, pipx, poetry,
pyenv, twine, virtualenv, and more. uv manages Python versions,
dependencies, scripts, tools, and projects.

%description -l pl.UTF-8
uv to bardzo szybki menedżer pakietów i projektów Pythonowych
napisany w Ruście. Stanowi zamiennik narzędzi pip, pip-tools, pipx,
poetry, pyenv, twine, virtualenv i innych. uv zarządza wersjami
Pythona, zależnościami, skryptami, narzędziami i projektami.

%package -n bash-completion-uv
Summary:	Bash completion for uv command
Summary(pl.UTF-8):	Bashowe dopełnianie składni dla polecenia uv
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-uv
Bash completion for uv command.

%description -n bash-completion-uv -l pl.UTF-8
Bashowe dopełnianie składni dla polecenia uv.

%package -n fish-completion-uv
Summary:	fish completion for uv command
Summary(pl.UTF-8):	Dopełnianie składni fisha dla polecenia uv
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	fish
BuildArch:	noarch

%description -n fish-completion-uv
fish completion for uv command.

%description -n fish-completion-uv -l pl.UTF-8
Dopełnianie składni fisha dla polecenia uv.

%package -n zsh-completion-uv
Summary:	Zsh completion for uv command
Summary(pl.UTF-8):	Zshowe dopełnianie składni dla polecenia uv
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	zsh
BuildArch:	noarch

%description -n zsh-completion-uv
Zsh completion for uv command.

%description -n zsh-completion-uv -l pl.UTF-8
Zshowe dopełnianie składni dla polecenia uv.

%prep
%setup -q -a1
%ifarch %{ix86} %{arm}
%patch -P0 -p1
%endif

export CARGO_HOME="$(pwd)/.cargo"
mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[source.crates-io]
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export CARGO_OFFLINE=true
export CARGO_TERM_VERBOSE=true
%ifarch %{ix86} %{arm}
export RUSTFLAGS="-C debuginfo=0 -C strip=none"
%endif

%cargo_build --frozen --bin uv --bin uvx

%if %{with tests}
cargo test --release --frozen --offline
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_bindir},%{bash_compdir},%{fish_compdir},%{zsh_compdir}}

install -p %{cargo_targetdir}/%{rust_target}/release/uv  $RPM_BUILD_ROOT%{_bindir}/uv
install -p %{cargo_targetdir}/%{rust_target}/release/uvx $RPM_BUILD_ROOT%{_bindir}/uvx

$RPM_BUILD_ROOT%{_bindir}/uv generate-shell-completion bash > $RPM_BUILD_ROOT%{bash_compdir}/uv
$RPM_BUILD_ROOT%{_bindir}/uv generate-shell-completion fish > $RPM_BUILD_ROOT%{fish_compdir}/uv.fish
$RPM_BUILD_ROOT%{_bindir}/uv generate-shell-completion zsh > $RPM_BUILD_ROOT%{zsh_compdir}/_uv

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md LICENSE-APACHE LICENSE-MIT README.md
%attr(755,root,root) %{_bindir}/uv
%attr(755,root,root) %{_bindir}/uvx

%files -n bash-completion-uv
%defattr(644,root,root,755)
%{bash_compdir}/uv

%files -n fish-completion-uv
%defattr(644,root,root,755)
%{fish_compdir}/uv.fish

%files -n zsh-completion-uv
%defattr(644,root,root,755)
%{zsh_compdir}/_uv
