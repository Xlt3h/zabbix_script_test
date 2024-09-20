import os
import subprocess

# Define paths and content
monitor_directory = '/home/rich/Documents/zabbix-scripts'  # Change this to your desired directory
sh_script_path = '/usr/local/bin/auto_exec_permission.sh'
service_file_path = '/etc/systemd/system/auto_exec_permission.service'
sh_script_content = f"""#!/bin/bash

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
"""

service_file_content = f"""[Unit]
Description=Automatically grants execution permission to new files in a directory
After=network.target

[Service]
ExecStart={sh_script_path} {monitor_directory}
Restart=always
WorkingDirectory={monitor_directory}

[Install]
WantedBy=multi-user.target
"""

# Function to run shell commands
def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

# Step 1: Install inotify-tools
print("Installing inotify-tools...")
run_command('sudo apt-get install -y inotify-tools')  # Change this for your package manager if needed

# Step 2: Create the shell script
print("Creating the shell script...")
with open(sh_script_path, 'w') as sh_file:
    sh_file.write(sh_script_content)

# Step 3: Make the shell script executable
print("Making the shell script executable...")
run_command(f'sudo chmod +x {sh_script_path}')

# Step 4: Create the systemd service file
print("Creating the systemd service file...")
with open(service_file_path, 'w') as service_file:
    service_file.write(service_file_content)

# Step 5: Reload systemd, enable, and start the service
print("Enabling and starting the service...")
run_command('sudo systemctl daemon-reload')
run_command(f'sudo systemctl enable {os.path.basename(service_file_path)}')
run_command(f'sudo systemctl start {os.path.basename(service_file_path)}')

# Step 6: Check the service status
print("Checking the service status...")
returncode, stdout, stderr = run_command(f'sudo systemctl status {os.path.basename(service_file_path)}')
print(stdout)

# Step 7: Check logs
print("Checking logs...")
returncode, stdout, stderr = run_command(f'journalctl -u {os.path.basename(service_file_path)} -f')
print(stdout)
