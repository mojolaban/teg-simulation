{ pkgs }: {
  deps = [
    pkgs.sqlite
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
}