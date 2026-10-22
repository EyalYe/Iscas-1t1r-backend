#!/bin/sh
# Build main.pdf with tectonic (self-contained LaTeX engine; runs bibtex itself).
# Usage: ./build.sh [path/to/tectonic]   (default: tectonic on PATH)
cd "$(dirname "$0")" && ${1:-tectonic} --keep-logs main.tex
