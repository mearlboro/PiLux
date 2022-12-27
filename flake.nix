/*
*/
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/release-22.11";
  inputs.nixos-generators.url = "github:nix-community/nixos-generators";
  inputs.nixos-generators.inputs.nixpkgs.follows = "nixpkgs";
  inputs.deploy.url = "github:serokell/deploy-rs";

  outputs = { self, nixpkgs, nixos-generators, deploy, ... }@inputs: {
    packages.x86_64-linux = { } // nixos-generators.packages.x86_64-linux // deploy.packages.x86_64-linux;
    nixosConfigurations.pi3 = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      system = "aarch64-linux";
      modules = [
        ./nix/pi3.nix
      ];
    };
    nixosConfigurations.pi4 = nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      system = "aarch64-linux";
      modules = [
        ./nix/pi4.nix
      ];
    };
    deploy = {
      fastConnection = true;
      sshUser = "deploy";
      magicRollback = false;
      autoRollback = false;
      nodes.pi3 = {
        hostname = "192.168.0.97";
        profiles.system = {
          user = "root";
          path = deploy.lib.aarch64-linux.activate.nixos self.nixosConfigurations.pi3;
        };
      };
      nodes.pi4 = {
        hostname = "192.168.0.98";
        profiles.system = {
          user = "root";
          path = deploy.lib.aarch64-linux.activate.nixos self.nixosConfigurations.pi4;
        };
      };
    };
  };
}
