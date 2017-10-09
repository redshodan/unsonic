#!/bin/bash


CMD="$1"
DIST="$2"
USER="$3"
HOME="$4"

grep -sq $USER /etc/passwd
if [ $? != 0 ]; then
    echo "** Adding user $USER as a service account"
    echo useradd -d $HOME -r -m $USER
    echo | useradd -d $HOME -r -m -U -p 'f' $USER
else
    echo "** User $USER already exists"
fi

if [ ! -d $HOME ]; then
    echo "** Creating home directory: $HOME"
    echo mkdir -p $HOME
    mkdir -p $HOME
    echo chown $USER $HOME
    chown $USER $HOME
    echo chmod 0755 $HOME
    chmod 0755 $HOME
else
    echo "** User's home dir, $HOME, already exists"
fi

if [ ! -f /etc/conf.d/unsonic ]; then
    echo "** Creating service configuration file /etc/conf.d/unsonic"
    echo cp $DIST/etc/unsonic.confd /etc/conf.d/unsonic
    cp $DIST/etc/unsonic.confd /etc/conf.d/unsonic
else
    echo "** Service configuration file already exists"
fi

if [ ! -f /etc/unsonic.ini ]; then
    echo "** Creating Unsonic configuration /etc/unsonic.ini"
    echo cp $DIST/etc/unsonic.ini.in /etc/unsonic.ini
    cp $DIST/etc/unsonic.ini.in /etc/unsonic.ini
    sed "s?UNSONIC_HOME?$HOME?" $DIST/etc/unsonic.ini.in > /etc/unsonic.ini
else
    echo "** Configuration file already exists"
fi

if [ ! -f /etc/systemd/system/unsonic.service ]; then
    echo "** Installing systemd service file"
    echo cp $DIST/etc/unsonic.service /etc/systemd/system/unsonic.service
    sed "s?CMD?$CMD?; s/User=/User=$USER/; s?WorkingDirectory=?WorkingDirectory=$HOME?" $DIST/etc/unsonic.service > /etc/systemd/system/unsonic.service
else
    echo "** Systemd service file already exists"
fi

echo "** Enabling Unsonic service"
echo systemctl enable unsonic
systemctl enable unsonic

echo
echo "Now edit /etc/unsonic/unsonic.ini and update the database location"
echo "and the music libraries. After that you can start unsonic with:"
echo "    systemctl start unsonic"
