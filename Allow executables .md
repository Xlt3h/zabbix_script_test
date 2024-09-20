# Packages needed
```bash
sudo apt-get install inotify-tools   # On Ubuntu/Debian
sudo yum install inotify-tools       # On CentOS/RHEL
```

# Monitor and grant executables background even after restart
## step 1
- create a file in /user/local/bin/auto_exec_permission.sh (auto_exec_permission is the name of the file)
    - sudo nano /usr/local/bin/auto_exec_permission.sh
## step 2 add this inside the nano dont forget to save and exit
```bash
#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <Directory to Monitor>"
  exit 1
fi

MONITOR_DIR="$1"

if ! command -v inotifywait &> /dev/null; then
  echo "inotifywait command not found! Please install inotify-tools package."
  exit 1
fi

inotifywait -m "$MONITOR_DIR" -e create -e moved_to |
    while read path action file; do
        chmod +x "$path$file"
        echo "Execution permission granted to: $path$file"
    done

```
## step 3 grant executable for this file
```bash
sudo chmod +x /usr/local/bin/auto_exec_permission.sh
```
## step 4 create systemd service file
```bash
sudo nano /etc/systemd/system/auto_exec_permission.service
```
## step 5 write this inside the file this will run as root
```ini
[Unit]
Description=Automatically grants execution permission to new files in a directory
After=network.target

[Service]
ExecStart=/usr/local/bin/auto_exec_permission.sh /path/to/your/directory
Restart=always
WorkingDirectory=/path/to/your/directory

[Install]
WantedBy=multi-user.target
```
## step 6 run this commands 
```bash
sudo systemctl daemon-reload
```
```bash
sudo systemctl enable auto_exec_permission.service
```
```bash
sudo systemctl start auto_exec_permission.service
```
```bash
sudo systemctl status auto_exec_permission.service
```
## check logs 
```bash
journalctl -u auto_exec_permission.service -f
```