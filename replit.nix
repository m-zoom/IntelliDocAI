{pkgs}: {
  deps = [
    pkgs.libxcrypt
    pkgs.bash
    pkgs.postgresql
    pkgs.openssl
  ];
}
