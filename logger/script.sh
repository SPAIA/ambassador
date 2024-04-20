sudo apt update
sudo apt upgrade
sudo apt install -y netcat-openbsd python3-pip python3-libcamera python3-venv python3-full libcap-dev python3-numpy python3-kms++ gcc-arm-linux-gnueabihf libgpiod2 libgpiod-dev xvfb
sudo raspi-config nonint do_i2c 1
sudo apt install build-essential cmake git pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev python3-pip python3-numpy -y
