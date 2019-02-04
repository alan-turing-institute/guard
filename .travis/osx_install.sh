#!/usr/bin/env bash

case "${PYTHON_VERSION}" in
  3.6)
    ;;
  3.7)
    brew update
    brew upgrade python
    ;;
esac

pip3 install -r requirements.txt
pip3 install pytest
