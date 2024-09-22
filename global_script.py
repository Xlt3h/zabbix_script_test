import os
import subprocess

# Define paths and contents
monitor_directory = "/dev/zabbix_telkom"  # Updated to zabbix_telkom
allow_run_file = os.path.join(monitor_directory, "allow_run.txt")
monitoring_script_path = "/usr/local/bin/auto_install_scripts.sh"
service_file_path = "/etc/systemd/system/auto_install_scripts.service"

# Monitoring script content
monitoring_script_content = f"""#!/bin/bash

# Check if the directory to monitor is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <Directory to Monitor>"
  exit 1
fi

MONITOR_DIR="$1"
INSTALL_DIR="/usr/local/bin"

# Check if the inotifywait command is available (part of inotify-tools package)
if ! command -v inotifywait &> /dev/null; then
  echo "inotifywait command not found! Please install inotify-tools package."
  exit 1
fi

# Function to process .sh files
process_scripts() {{
  for file in "$MONITOR_DIR"/*.sh; do
    if [ -f "$file" ]; then
      chmod +x "$file"
      cp "$file" "$INSTALL_DIR/"
      echo "Execution permission granted and $(basename "$file") copied to $INSTALL_DIR"
    fi
  done
}}

# Process existing .sh files at startup
process_scripts

# Use inotifywait to monitor the directory for new .sh files
inotifywait -m "$MONITOR_DIR" -e create -e moved_to |
    while read path action file; do
        if [[ "$file" == *.sh ]]; then
            # Give execution permission to the new .sh file
            chmod +x "$path$file"

            # Copy the .sh file to the install directory
            cp "$path$file" "$INSTALL_DIR/$file"

            echo "Execution permission granted and $file copied to $INSTALL_DIR"
        fi
    done
}}

# Call the function to process existing files
process_scripts
"""

# Service file content
service_file_content = f"""[Unit]
Description=Automatically sets execution permissions and installs new scripts
After=network.target

[Service]
ExecStart={monitoring_script_path} {monitor_directory}
Restart=always

[Install]
WantedBy=multi-user.target
"""

# Create the monitoring script
with open(monitoring_script_path, 'w') as script_file:
    script_file.write(monitoring_script_content)

# Make the monitoring script executable
subprocess.run(["chmod", "+x", monitoring_script_path])

# Create the systemd service file
with open(service_file_path, 'w') as service_file:
    service_file.write(service_file_content)

# Reload systemd and enable the service
subprocess.run(["systemctl", "daemon-reload"])
subprocess.run(["systemctl", "enable", "auto_install_scripts.service"])
subprocess.run(["systemctl", "start", "auto_install_scripts.service"])

# Step to handle allow_run.txt
if not os.path.exists(allow_run_file):
    # Create allow_run.txt and set the initial content
    with open(allow_run_file, 'w') as file:
        file.write("monitor_directory=false\nallow_global=false\n")
        print(f"Created {allow_run_file} with initial content.")
else:
    # Check for allow_global line and append it if not present
    with open(allow_run_file, 'r+') as file:
        content = file.read()
        if "allow_global=true" not in content:
            file.write("\nallow_global=true\n")
            print("Appended allow_global=true to allow_run.txt.")

print("Monitoring script and systemd service created successfully.")
print(f"Monitoring directory: {monitor_directory}")
print("Service is now running in the background.")
