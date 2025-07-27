sudo apt update
sudo apt upgrade -y

# Install necessary packages
sudo apt install -y libcamera-apps libcamera-dev screen python3-venv python3-full netcat-openbsd python3-pip python3-libcamera libcap-dev python3-numpy python3-kms++ gcc-arm-linux-gnueabihf libgpiod2 libgpiod-dev xvfb python3-picamera2 vlc-bin
sudo apt install -y build-essential cmake git pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev i2c-tools libgtk-3-dev libatlas-base-dev gfortran python3-dev libopencv-dev python3-opencv

# Enable I2C and SPI
sudo raspi-config nonint do_i2c 1
sudo raspi-config nonint do_spi 0

# Disable HDMI
sudo sed -i '$i /usr/bin/tvservice -o' /etc/rc.local

# Disable Bluetooth
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
sudo systemctl disable hciuart

echo 'dtoverlay=dwc2,dr_mode=host' | sudo tee -a /boot/config.txt

sudo ifconfig eth0 down

sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy
sudo systemctl disable bluetooth


# Load LED control modules
sudo modprobe leds_gpio
echo "leds_gpio" | sudo tee -a /etc/modules

# Turn off status LEDs if they exist
if [ -e /sys/class/leds/ACT/brightness ]; then
    echo 0 | sudo tee /sys/class/leds/ACT/brightness
fi

if [ -e /sys/class/leds/default-on/brightness ]; then
    echo 0 | sudo tee /sys/class/leds/default-on/brightness
fi

if [ -e /sys/class/leds/mmc0/brightness ]; then
    echo 0 | sudo tee /sys/class/leds/mmc0/brightness
fi


source .venv/bin/activate