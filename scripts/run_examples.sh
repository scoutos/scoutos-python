#!/usr/bin/env bash

set -e
set -u

ROOT_DIR=$(pwd)
EXAMPLES_DIR="./examples"

for example_dir in "$EXAMPLES_DIR"/*; do
  if [ -d "$example_dir" ] && [ "$example_dir" != "./examples/load_from_yaml" ]; then
    echo "Running test for example: $example_dir"
    cd "$example_dir" || exit
    make setup
    make test
    make teardown
    cd "$ROOT_DIR" || exit
  fi
done

echo "All tests completed successfully 🎉"
