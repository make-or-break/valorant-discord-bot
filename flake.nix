{
  description = "get valorant rank from API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:


    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in
      rec {

        # Use nixpkgs-fmt for `nix fmt'
        formatter = pkgs.nixpkgs-fmt;

        defaultPackage = packages.valorant-discord-bot;
        packages = flake-utils.lib.flattenTree rec {

          valorant-discord-bot = with pkgs.python3Packages;
            pkgs.python3Packages.buildPythonPackage rec {
              pname = "valorant-discord-bot";
              version = "0.1";
              propagatedBuildInputs = [ discordpy requests sqlalchemy ];
              doCheck = false;
              src = self;
              # removes install_requires from the setup.py
              # version numbers of discord.py are still broken
              preBuild = ''
                sed -i '8d' setup.py
              '';
              meta = with pkgs.lib; {
                description = "get valorant rank from API";
                homepage = "https://github.com/MayNiklas/discord-bot-valorant-rank/";
                platforms = platforms.unix;
                maintainers = with maintainers; [ mayniklas ];
              };
            };

        };


      });
}
