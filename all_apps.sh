#!/bin/bash

# Declare an associative array to store unique applications
declare -A app_list

# Function to add an app to the list if it's not already added
add_to_app_list() {
  local app="$1"
  if [[ -z "${app_list[$app]}" ]]; then
    app_list["$app"]=1
    echo "$app"
  fi
}

# List applications found in /usr/share/applications or /usr/local/share/applications
echo "Applications found in /usr/share/applications and /usr/local/share/applications:"
for app in $(find /usr/share/applications /usr/local/share/applications -name '*.desktop' -exec basename {} .desktop \;); do
  add_to_app_list "$app"
done

# List applications manually installed in /opt
echo -e "\nApplications found in /opt:"
for app in $(ls /opt 2>/dev/null); do
  add_to_app_list "$app"
done

# List binaries in /usr/bin that are commonly associated with installed applications
echo -e "\nApplications in /usr/bin:"
for app in $(ls /usr/bin); do
  if command -v "$app" &> /dev/null; then
    add_to_app_list "$app"
  fi
done

# Check snap packages for installed applications
if command -v snap &> /dev/null; then
  echo -e "\nSnap applications:"
  for app in $(snap list | awk 'NR>1 {print $1}'); do
    add_to_app_list "$app"
  done
fi

# Check flatpak for installed applications
if command -v flatpak &> /dev/null; then
  echo -e "\nFlatpak applications:"
  for app in $(flatpak list --app | awk '{print $1}'); do
    add_to_app_list "$app"
  done
fi

# Check for AppImages in ~/Applications
echo -e "\nAppImages found in ~/Applications:"
if [ -d "$HOME/Applications" ]; then
  for app in $(ls "$HOME/Applications"/*.AppImage 2>/dev/null | xargs -n 1 basename); do
    add_to_app_list "${app%.AppImage}"
  done
else
  echo "No AppImages directory found"
fi

# Find running applications and add them to the list if they are not already there
echo -e "\nRunning applications (not already listed):"
for app in $(ps -eo comm | sort | uniq); do
  if [[ -z "${app_list[$app]}" ]]; then
    add_to_app_list "$app"
  fi
done

