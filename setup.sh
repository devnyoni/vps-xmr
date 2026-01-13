#!/bin/bash
# setup.sh

echo "--- Inaanza kusanidi mazingira ya VPS ---"
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst python3-flask python3-libvirt

# Hakikisha Libvirt inawaka
sudo systemctl enable libvirtd
sudo systemctl start libvirtd

# Ongeza ruhusa kwa user
sudo adduser $USER libvirt
sudo adduser $USER kvm

echo "--- Usanidi umekamilika! ---"
