{
  description = "valorant discord bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-21.11";
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

          valorant-discord-bot = with pkgs.python38Packages;
            pkgs.python38Packages.buildPythonPackage rec {
              pname = "valorant-discord-bot";
              version = "0.1";

              src = self;
              # 403 Forbidden when using requests 2.27.0
              # -> had to use nixos-21.11 as flake input!
              propagatedBuildInputs = [ discordpy requests sqlalchemy ];
              doCheck = false;

              pythonImportsCheck = [
                "database.sql_scheme"
                "database.sql_statements"

                "valorant"
              ];

              # removes install_requires from the setup.py
              # version numbers of discord.py are still broken
              preBuild = ''
                sed -i '8d' setup.py
              '';

              meta = with pkgs.lib; {
                description = "valorant discord bot";
                homepage = "https://github.com/MayNiklas/discord-bot-valorant-rank/";
                platforms = platforms.unix;
                maintainers = with maintainers; [ mayniklas ];
              };
            };

        };


      });
}
