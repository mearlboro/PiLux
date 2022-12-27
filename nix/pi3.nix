{ inputs, pkgs, lib, ... }:
{
  imports = [
    ./base-pi.nix
    #inputs.nixos-generators.nixosModules.sd-aarch64-installer
    #inputs.nixos-generators.nixosModules.sd-aarch64
  ];
  boot.kernelPackages = pkgs.linuxPackages_rpi3;
}

