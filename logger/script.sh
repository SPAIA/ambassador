sudo apt update
sudo apt upgrade
sudo apt install -y netcat-openbsd python3-pip python3-libcamera python3-venv python3-full libcap-dev python3-numpy python3-kms++ gcc-arm-linux-gnueabihf libgpiod2 libgpiod-dev xvfb
sudo raspi-config nonint do_i2c 1