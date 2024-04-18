#!/usr/bin/env bash

set -e
set -u

ROOT_DIR=$(pwd)
EXAMPLES_DIR="./examples"

for example_dir in "$EXAMPLES_DIR"/*; do
  if [ -d "$example_dir" ]; then
    echo ""
    echo "Running test for example: $example_dir"
    echo "---"
    cd "$example_dir" || exit
    make setup
    make test
    make teardown
    echo "OK"
    cd "$ROOT_DIR" || exit
  fi
done

echo "All tests completed successfully 🎉"
