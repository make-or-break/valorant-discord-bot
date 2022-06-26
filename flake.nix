{
  description = "valorant discord bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:

    {
      nixosModules.default = self.nixosModules.valorant-discord-bot;
      nixosModules.valorant-discord-bot = { lib, pkgs, config, ... }:
        with lib;

        let cfg = config.services.valorant-discord-bot;
        in
        {

          options.services.valorant-discord-bot = {

            enable = mkEnableOption "valorant-discord-bot";

            dataDir = mkOption {
              type = types.str;
              default = "/var/lib/valorant-discord-bot";
              description = ''
                The directory where valorant-discord-bot stores its data files. If left as the default value this directory will automatically be created before the discord server starts, otherwise the sysadmin is responsible for ensuring the directory exists with appropriate ownership and permissions.
              '';
            };

            envfile = mkOption {
              type = types.str;
              default = "/var/src/secrets/valorant-discord-bot/envfile";
              description = ''
                The location of the envfile containing secrets
              '';
            };

            user = mkOption {
              type = types.str;
              default = "valorant-discord-bot";
              description = "User account under which valorant-discord-bot runs.";
            };

            group = mkOption {
              type = types.str;
              default = "valorant-discord-bot";
              description = "Group under which valorant-discord-bot runs.";
            };

          };

          config = mkIf cfg.enable {

            systemd.services.valorant-discord-bot = {
              description = "A discord bot for our valorant group";
              wantedBy = [ "multi-user.target" ];
              serviceConfig = mkMerge [
                {
                  EnvironmentFile = [ cfg.envfile ];
                  User = cfg.user;
                  Group = cfg.group;
                  WorkingDirectory = cfg.dataDir;
                  ExecStart = "${self.packages."${pkgs.system}".valorant-discord-bot}/bin/valorant-discord-bot";
                  Restart = "on-failure";
                }
                (mkIf (cfg.dataDir == "/var/lib/valorant-discord-bot") {
                  StateDirectory = "valorant-discord-bot";
                })
              ];

            };

            users.users = mkIf (cfg.user == "valorant-discord-bot") {
              valorant-discord-bot = {
                isSystemUser = true;
                group = cfg.group;
                description = "valorant-discord-bot system user";
              };
            };

            users.groups =
              mkIf (cfg.group == "valorant-discord-bot") { valorant-discord-bot = { }; };

          };
          meta = { maintainers = with lib.maintainers; [ mayniklas ]; };
        };
    }

    //

    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in
      rec {

        # Use nixpkgs-fmt for `nix fmt'
        formatter = pkgs.nixpkgs-fmt;

        defaultPackage = packages.valorant-discord-bot;
        packages = flake-utils.lib.flattenTree rec {

          valorant-discord-bot = with pkgs.python310Packages;
            buildPythonPackage rec {
              pname = "valorant-discord-bot";
              version = "0.1";

              src = self;
              propagatedBuildInputs =
                let
                  # we want to use discordpy 2.0.0, but it's not available in nixpkgs yet (it's still in beta)
                  discordpy_2 = (discordpy.overrideAttrs
                    (old: rec {
                      pname = "discord.py";
                      version = "2.0.0a4370+g868476c9";
                      src = pkgs.fetchFromGitHub {
                        owner = "Rapptz";
                        repo = pname;
                        rev = "903e2e64e9182b8d3330ef565af7bb46ff9f04da";
                        sha256 = "sha256-u17sG3mjJf19euZ0CHvJwnvhb16F3WyAQt/w+RZFu1Y=";
                      };
                    }));
                  # requests 2.27.0 is terribly broken, so we use 2.18.0 instead
                  requests_2_28_0 = (requests.overrideAttrs
                    (old: rec{
                      pname = "requests";
                      version = "2.28.0";
                      src = fetchPypi {
                        inherit pname version;
                        hash = "sha256-1WhyOn69JYddjR6vXfoGjNL8gZSy5IPXsffIGRjb7Gs=";
                      };
                    }));
                in
                [
                  discordpy_2
                  requests_2_28_0
                  sqlalchemy
                ];

              doCheck = false;
              pythonImportsCheck = [
                "database.sql_scheme"
                "database.sql_statements"

                "valorant"
              ];

              # removes install_requires from the setup.py
              # version numbers of discord.py are still broken
              preBuild = ''
                sed -i '10d' setup.py
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
