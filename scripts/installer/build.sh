#!/bin/sh

binary_zip_filename="cfn-lint.zip"

set -eux

echo "Making Folders"
mkdir -p ./build/src
rm -Rf ./build/src/pyinstaller-output
mkdir -p ./build/output/pyinstaller-output
cd ./build

# Copying cfn-lint-cli source code
echo "Copying Source"
for item in ../[!.]*; do
  if [ "$(basename "$item")" != "local" -a "$(basename "$item")" != "build" -a "$(basename "$item")" != "venv" ]; then
    cp -r "$item" ./src/
  fi
done

echo "Installing Python Libraries"
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r src/requirements/base.txt

echo "Installing PyInstaller"
./venv/bin/pip install -r src/requirements/pyinstaller-build.txt
./venv/bin/pip check

# Building the binary using pyinstaller
echo "Building Binary"
cd src
echo "cfnlint.spec content is:"
cat scripts/installer/cfnlint.spec
../venv/bin/python -m PyInstaller --clean scripts/installer/cfnlint.spec

# Organizing the pyinstaller-output folder
mkdir pyinstaller-output
dist_folder="cfn-lint"
echo "dist_folder=$dist_folder"
mv "dist/$dist_folder" pyinstaller-output/dist
echo "Copying Binary"
cd ..
cp -r src/pyinstaller-output/* output/pyinstaller-output

echo "Packaging Binary"
cd output
cd pyinstaller-output
cd dist
zip -r ../../"$binary_zip_filename" ./*
