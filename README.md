sudo find odoolms/  -type d -exec chmod 755 {} \;
sudo find odoolms/  -type f -exec chmod 644 {} \;
sudo find odoolms/  -type d -exec chown daniel:daniel {} \;
sudo find odoolms/  -type f -exec chown daniel:daniel {} \;
