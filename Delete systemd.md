# To delete the systemd service, follow these steps:

## 1. Stop the Service
- First, stop the service if it's currently running:

```bash
sudo systemctl stop auto_exec_permission.service
```
##  2. Disable the Service
 Disable the service so it doesn't start on boot:


```bash
sudo systemctl disable auto_exec_permission.service
```
## 3. Remove the Service File
Delete the service file from /etc/systemd/system/:

```bash
sudo rm /etc/systemd/system/auto_exec_permission.service
```

## 4. Reload systemd Daemon
After removing the service file, reload the systemd daemon to reflect the changes:

```bash
sudo systemctl daemon-reload
```

## 5. Verify the Service is Removed
Check if the service is no longer active:

```bash

sudo systemctl status auto_exec_permission.service
```
This should show that the service no longer exists.

## Optional: Remove the Script
If you also want to remove the script (/usr/local/bin/auto_exec_permission.sh), you can delete it as well:

```bash

sudo rm /usr/local/bin/auto_exec_permission.sh
```
This will clean up both the service and the script from your system.