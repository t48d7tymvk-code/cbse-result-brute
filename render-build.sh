#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Install Chrome
STORAGE_DIR=/opt/render/project/src/.render/chrome
if [ ! -d "$STORAGE_DIR" ]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR
  cd $STORAGE_DIR
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x google-chrome-stable_current_amd64.deb .
else
  echo "...Using cached Chrome"
fi
