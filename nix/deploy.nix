{ pkgs, ... }:
{
  users.users.deploy = {
    uid = 2001;
    group = "adm";
    description = "deploy user";
    isNormalUser = true;
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBO6HhFca5EnUD50SlOMfL/1iL8xLxmYEGPw+bs79Bv+ chris@github"
    ];
    extraGroups = [ "deploy" ];
  };
  users.groups.deploy.gid = 9001;
  security.doas.extraRules = [
    { users = [ "deploy" ]; noPass = true; }
  ];
  security.sudo.extraRules = [{
    users = [ "deploy" ];
    commands = [{
      command = "ALL";
      options = [ "NOPASSWD" ]; # "SETENV" # Adding the following could be a good idea
    }];
  }];
  nix.settings = {
    allowed-users = [ "deploy" ];
    trusted-users = [ "deploy" ];
  };
}

