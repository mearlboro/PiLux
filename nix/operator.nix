{ pkgs, ... }:
{
  users.users.operator = {
    uid = 2000;
    # password: asdasd
    hashedPassword = "$y$j9T$SsVkTPaU6F3IBS07IB9D7.$KiQCkM28K7HVZhatV/qGCMiOLLc65ygXFgjFNYIj1X5";
    description = "operator user";
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    packages = with pkgs; [
      vim
      tmux
      git
      fzf
      inetutils

      ranger
      monitor
    ];
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBO6HhFca5EnUD50SlOMfL/1iL8xLxmYEGPw+bs79Bv+ chris@github"
    ];
  };
  nix.settings.allowed-users = [ "operator" ];

  security.doas.extraRules = [
    { users = [ "operator" ]; cmd = "${pkgs.systemd}/bin/journalctl"; noPass = true; }
    { users = [ "operator" ]; cmd = "${pkgs.systemd}/bin/machinectl"; noPass = true; }
    { users = [ "operator" ]; cmd = "${pkgs.systemd}/bin/systemctl"; noPass = true; }
    { users = [ "operator" ]; persist = true; }
  ];
}
