import os
import subprocess

# Define paths and content
monitor_directory = '/dev/zabbix_telkom'
allow_run_file = os.path.join(monitor_directory, 'allow_run.txt')
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

# Step 1: Create the zabbix_telkom directory if it doesn't exist
if not os.path.exists(monitor_directory):
    print(f"Creating directory {monitor_directory}...")
    os.makedirs(monitor_directory)

# Step 2: Check if allow_run.txt exists and handle its content
if os.path.exists(allow_run_file):
    with open(allow_run_file, 'r') as file:
        content = file.read().strip()
        if content == "monitor_directory=true":
            print("monitor_directory is already set to true. Exiting the script.")
            exit(0)  # Exit if it's already true
else:
    print(f"Creating {allow_run_file} with monitor_directory=false...")
    with open(allow_run_file, 'w') as file:
        file.write("monitor_directory=false")

# Step 3: Set monitor_directory to true
print("Setting monitor_directory to true...")
with open(allow_run_file, 'w') as file:
    file.write("monitor_directory=true")

# Step 4: Install inotify-tools if not installed
print("Installing inotify-tools...")
run_command('sudo apt-get install -y inotify-tools')

# Step 5: Create the shell script
print("Creating the shell script...")
with open(sh_script_path, 'w') as sh_file:
    sh_file.write(sh_script_content)

# Step 6: Make the shell script executable
print("Making the shell script executable...")
run_command(f'sudo chmod +x {sh_script_path}')

# Step 7: Create the systemd service file
print("Creating the systemd service file...")
with open(service_file_path, 'w') as service_file:
    service_file.write(service_file_content)

# Step 8: Reload systemd, enable, and start the service
print("Enabling and starting the service...")
run_command('sudo systemctl daemon-reload')
run_command(f'sudo systemctl enable {os.path.basename(service_file_path)}')
run_command(f'sudo systemctl start {os.path.basename(service_file_path)}')

# Step 9: Check the service status
print("Checking the service status...")
returncode, stdout, stderr = run_command(f'sudo systemctl status {os.path.basename(service_file_path)}')
print(stdout)

# # Step 10: Check logs
# print("Checking logs...")
# returncode, stdout, stderr = run_command(f'journalctl -u {os.path.basename(service_file_path)} -f')
# print(stdout)
