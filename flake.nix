# flake.nix
{
  description = "JSON Parser development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pytest
          pytest-cov
          black
          flake8
          mypy
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            git
            
            # Development tools
            tree
            ripgrep
            fd
            
            # These are planned for future C port
            #gcc
            #gdb
            #valgrind
            
            # Documentation
            man-pages
          ];

          shellHook = ''
            echo "JSON Parser Development Environment"
            echo "Python version: $(python --version)"
            echo "Available commands:"
            echo "  pytest      - Run tests"
            echo "  black       - Format code"
            echo "  flake8      - Lint code"
            echo "  mypy        - Type checking"
            echo ""
            echo "Project structure:"
            echo "  src/        - Source code"
            echo "  tests/      - Test files"
            echo "  examples/   - Example JSON files"
            echo ""
            
            # Set up Python path
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            
            # Create directories if they don't exist
            mkdir -p src tests examples tests/fixtures/valid tests/fixtures/invalid
            
            # Initialize __init__.py files
            touch src/__init__.py tests/__init__.py
          '';
        };
      });
}
