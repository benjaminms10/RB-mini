# debug_icon.py
import os

print("=" * 50)
print("ICON DEBUG INFO")
print("=" * 50)

# Get current directory
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {base_dir}")

# Check the icon path
icon_path = os.path.join(base_dir, "resources", "icons", "RB-icon.png")
print(f"Icon path: {icon_path}")

# Check if file exists
if os.path.exists(icon_path):
    print("✅ File EXISTS!")
    print(f"File size: {os.path.getsize(icon_path)} bytes")
else:
    print("❌ File DOES NOT EXIST!")

# List all files in the icons folder
icons_dir = os.path.join(base_dir, "v1", "resources", "icons")
if os.path.exists(icons_dir):
    print(f"\nFiles in {icons_dir}:")
    for file in os.listdir(icons_dir):
        print(f"  - {file}")
else:
    print(f"\n❌ Folder does not exist: {icons_dir}")

print("=" * 50)