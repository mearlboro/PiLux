{ inputs, pkgs, lib, ... }:
{
  imports = [
    ./operator.nix
    ./deploy.nix
    inputs.nixos-generators.nixosModules.sd-aarch64-installer
    #inputs.nixos-generators.nixosModules.sd-aarch64
  ];
  # Disable ZFS
  #boot.supportedFilesystems = lib.mkForce [ ];
  boot.supportedFilesystems = lib.mkForce [ "btrfs" "reiserfs" "vfat" "f2fs" "xfs" "ntfs" "cifs" "ext4" "vfat" ];

  # workaround for sun4i-drm missing
  # see: https://github.com/NixOS/nixpkgs/issues/154163
  nixpkgs.overlays = [
    (final: super: {
      makeModulesClosure = x:
        super.makeModulesClosure (x // { allowMissing = true; });
    })
  ];
  security.doas.enable = true;
  services.openssh = {
    enable = true;
    openFirewall = true;
  };

  boot = {
    #kernelPackages = pkgs.linuxPackages_rpi4;
    #kernelPackages = pkgs.linuxPackages_rpi3;
    tmpOnTmpfs = true;
    initrd.availableKernelModules = [ "usbhid" "usb_storage" ];
    # ttyAMA0 is the serial console broken out to the GPIO
    kernelParams = [
      "8250.nr_uarts=1"
      "console=ttyAMA0,115200"
      "console=tty1"
      # A lot GUI programs need this, nearly all wayland applications
      "cma=128M"
    ];
  };

  # imcompatible with generic-extlinux-compatible
  #boot.loader.raspberryPi = {
  #  enable = true;
  #  version = 4;
  #};
  boot.loader.grub.enable = false;

  environment.systemPackages = with pkgs; [
    gcc
    python310Packages.spidev
    python310Packages.bpython
    python3
  ];

  # Required for the Wireless firmware
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;
  networking.wireless.userControlled.enable = true;
  # create with `wpa_supplicant YOUR_SSID YOUR_PASSWORD` and copy the `psk` hex into here;
  # NOTE: change this to your own wifi network
  networking.wireless.networks."YOUR WIFI SSID".pskRaw = "3f18339a05d7bea1237b8fa267258b4ed2d909ccedf39392ecf61d8763f4fa69";

  # Keep store small
  nix = {
    settings = {
      auto-optimise-store = true;
      experimental-features = [ "nix-command" "flakes" ];
    };
    gc = {
      automatic = true;
      dates = "weekly";
      options = "--delete-older-than 30d";
    };
    # Free up to 1GiB whenever there is less than 100MiB left.
    extraOptions = ''
      min-free = ${toString (100 * 1024 * 1024)}
      max-free = ${toString (1024 * 1024 * 1024)}
    '';
  };
  system.stateVersion = "22.11";
}

