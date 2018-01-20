#!/bin/bash

CMD="$1"
DIST="$2"
USER="$3"
HOME="$4"

echo "*******************************************************"
echo "  This will install Unsonic as a service."
read -p "  Do you wish to continue? (Y/y) " CONTINUE

if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
    echo "Exiting..."
    exit -1
fi

echo

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

if [ ! -d /var/log/unsonic ]; then
    echo "** Setting up logging directory"
    echo mkdir /var/log/unsonic
    mkdir /var/log/unsonic
    echo chown $USER /var/log/unsonic
    chown $USER /var/log/unsonic
else
    echo "** Logging directory already exists"
fi

if [ -d /etc/conf.d ]; then
    CONFD="/etc/conf.d"
elif [ -d /etc/default ]; then
    CONFD="/etc/default"
else
    echo "Failed to find the proper service configuration directory"
    exit 1
fi

if [ ! -f /etc/unsonic.ini ]; then
    echo "** Creating Unsonic configuration /etc/unsonic.ini"
    echo cp $DIST/etc/production.ini /etc/unsonic.ini
    sed "s?UNSONIC_HOME?$HOME?" $DIST/etc/production.ini > /etc/unsonic.ini
else
    echo "** Configuration file already exists"
fi

if [ ! -f $CONFD/unsonic ]; then
    echo "** Creating service configuration file $CONFD/unsonic"
    echo cp $DIST/etc/unsonic.confd $CONFD/unsonic
    cp $DIST/etc/unsonic.confd $CONFD/unsonic
else
    echo "** Service configuration file already exists"
fi

if [ ! -f /etc/systemd/system/unsonic.service ]; then
    echo "** Installing systemd service file"
    echo cp $DIST/etc/unsonic.service /etc/systemd/system/unsonic.service
    sed "s?CMD?$CMD?; s/User=/User=$USER/; s?CONFD?$CONFD?; s?WorkingDirectory=?WorkingDirectory=$HOME?" $DIST/etc/unsonic.service > /etc/systemd/system/unsonic.service
else
    echo "** Systemd service file already exists"
fi

echo "** Enabling Unsonic service"
echo systemctl enable unsonic
systemctl enable unsonic

echo
echo "Now edit /etc/unsonic.ini and update the database location"
echo "and the music libraries. Then sync the music directory with:"
echo "    su unsonic -c 'unsonic sync'"
echo "Now you may start unsonic with:"
echo "    systemctl start unsonic"
