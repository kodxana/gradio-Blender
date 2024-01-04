import gradio as gr
import subprocess
import os
import psutil
import requests
import tarfile
import shutil
import time
import glob
from gradio import File

# Define the download links for each version
dl_link = {
"Blender 2.79b": "https://download.blender.org/release/Blender2.79/blender-2.79b-linux-glibc219-x86_64.tar.bz2",
"Blender 2.80": "https://download.blender.org/release/Blender2.80/blender-2.80-linux-glibc217-x86_64.tar.bz2",
"Blender 2.81": "https://download.blender.org/release/Blender2.81/blender-2.81-linux-glibc217-x86_64.tar.bz2",
"Blender 2.82a": "https://download.blender.org/release/Blender2.82/blender-2.82a-linux64.tar.xz",
"Blender 2.83.0": "https://download.blender.org/release/Blender2.83/blender-2.83.0-linux64.tar.xz",
"Blender 2.83.3": "https://download.blender.org/release/Blender2.83/blender-2.83.3-linux64.tar.xz",
"Blender 2.90alpha (expiremental)": "https://blender.community/5edccfe69c122126f183e2ad/download/5ef635439c12214ca244be6b",
"Blender 2.90" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender2.90/blender-2.90.0-linux64.tar.xz",
"Blender 2.91" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender2.91/blender-2.91.0-linux64.tar.xz",
"Blender 2.92" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender2.92/blender-2.92.0-linux64.tar.xz",
"Blender 2.93" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender2.93/blender-2.93.0-linux64.tar.xz",
"Blender 3.0" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.0/blender-3.0.0-linux-x64.tar.xz",
"Blender 3.1" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.1/blender-3.1.0-linux-x64.tar.xz",
"Blender 3.2" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.2/blender-3.2.0-linux-x64.tar.xz",
"Blender 3.3" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.3/blender-3.3.0-linux-x64.tar.xz",
"Blender 3.4" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.4/blender-3.4.0-linux-x64.tar.xz",
"Blender 3.5" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.5/blender-3.5.0-linux-x64.tar.xz",
"Blender 3.6" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender3.6/blender-3.6.0-linux-x64.tar.xz",
"Blender 4.0" : "https://ftp.halifax.rwth-aachen.de/blender/release/Blender4.0/blender-4.0.1-linux-x64.tar.xz",
}

# Helper function to get formatted size
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# Function to get system and GPU info
def get_system_info():
    svmem = psutil.virtual_memory()
    system_info = f"Total: {get_size(svmem.total)}\nAvailable: {get_size(svmem.available)}\nUsed: {get_size(svmem.used)}\nPercentage: {svmem.percent}%"
    
    # Get GPU info using subprocess
    gpu_info = subprocess.run(["nvidia-smi", "--query-gpu=gpu_name,driver_version,memory.total,memory.free,memory.used", "--format=csv,noheader"], capture_output=True, text=True).stdout
    # Clean up the GPU info
    gpu_info = gpu_info.strip().replace('\n', ' | ')
    
    return system_info, gpu_info

# Define a function to save the current Blender version to a file
def save_current_version(version):
    with open('current_blender_version.txt', 'w') as f:
        f.write(version)

# Define a function to get the current Blender version from the file
def get_current_blender_version():
    if os.path.exists('current_blender_version.txt'):
        with open('current_blender_version.txt', 'r') as f:
            return f.read()
    else:
        return "No Blender version is currently set."


def wipe_blender():
    if os.path.exists('blender'):
        shutil.rmtree('blender')
        os.remove('current_blender_version.txt')  # Remove the current version file
        return "Existing Blender installation has been removed."
    else:
        return "No Blender installation found to remove."


def download_and_setup_blender(version, wipe_current=False):
    # Wipe the current Blender installation if requested
    if wipe_current:
        wipe_status = wipe_blender()
    else:
        wipe_status = "No wipe requested."
    
    current_version = get_current_blender_version()
    status_message = f"Current Version: {current_version}\n{wipe_status}\n"

    dl = dl_link[version]
    filename = os.path.basename(dl)
    
    # Download the Blender tarball
    response = requests.get(dl, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.raw.read())

        if filename.endswith(('.tar.bz2', '.tar.xz')):
            blender_dir = 'blender'
            if os.path.exists(blender_dir):
                shutil.rmtree(blender_dir)
            os.makedirs(blender_dir)

            with tarfile.open(filename) as tar:
                # Extract the tarball
                tar.extractall(path=blender_dir)
                # Find the extracted directory
                extracted_dir = next(os.walk(blender_dir))[1][0]
                extracted_path = os.path.join(blender_dir, extracted_dir)
                # Move the contents up a level if necessary
                if extracted_dir.startswith('blender'):
                    for content in os.listdir(extracted_path):
                        shutil.move(os.path.join(extracted_path, content), blender_dir)
                    shutil.rmtree(extracted_path)

            os.remove(filename)  # Clean up the downloaded tarball file


            # Setup GPU settings file
            gpu_setup = """
import bpy
import re

# Set the rendering to GPU if available
scene = bpy.context.scene
scene.cycles.device = 'GPU'

# Get the preferences for Cycles
prefs = bpy.context.preferences
prefs.addons['cycles'].preferences.get_devices()
cprefs = prefs.addons['cycles'].preferences

# Print current preferences
print(cprefs)

# Try to set the compute device types if available
for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
    try:
        cprefs.compute_device_type = compute_device_type
        print('Device found:', compute_device_type)
        break
    except TypeError:
        pass

# Enable all CPU and GPU devices except for Intel integrated graphics
for device in cprefs.devices:
    if not re.match('intel', device.name, re.I):
        print('Activating device:', device.name)
        device.use = True
"""
            with open('blender/setgpu.py', 'w') as f:
                f.write(gpu_setup)

            # Save the new current version
            save_current_version(version)
            status_message += f"Downloaded and set up Blender version {version} successfully."
        else:
            status_message += "Failed to extract Blender."
    else:
        status_message += "Failed to download Blender."

    return status_message

def list_blend_files():
    blend_dir = '/workspace/blend'
    if not os.path.exists(blend_dir):
        return []
    return [file for file in os.listdir(blend_dir) if file.endswith('.blend')]


def render_single_frame(blender_file, selected_file_name):
    workspace_dir = '/workspace'
    os.makedirs(workspace_dir, exist_ok=True)

    # Determine the path of the blend file based on user input
    if selected_file_name:
        # Use the file selected from the dropdown
        blend_file_path = os.path.join('/workspace/blend', selected_file_name)
    elif blender_file is not None:
        # Generate a unique file name for the uploaded file
        timestamp = int(time.time())
        blend_file_name = f"uploaded_blend_{timestamp}.blend"
        blend_file_path = os.path.join(workspace_dir, blend_file_name)
        with open(blend_file_path, 'wb') as file:
            file.write(blender_file)
    else:
        return "No file provided.", None, ""

    output_file_base_path = os.path.join(workspace_dir, "frame")

    command = [
        "./blender/blender", "-P", "./blender/setgpu.py", "-b", blend_file_path,
        "-o", output_file_base_path, "-f", "1"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Construct the expected output file name
        rendered_file_name = "frame0001.png"
        rendered_file_path = os.path.join(workspace_dir, rendered_file_name)

        # Blender logs
        blender_logs = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        if os.path.exists(rendered_file_path):
            return "Rendered successfully.", rendered_file_path, blender_logs
        else:
            return "Rendered but file not found.", None, blender_logs
    except subprocess.CalledProcessError as e:
        return "An error occurred: " + e.stderr.decode(), None, f"Error logs:\n{e.stderr.decode()}"
    finally:
        # Clean up the uploaded file if it was used
        if blender_file is not None and os.path.exists(blend_file_path):
            os.remove(blend_file_path)

def update_blend_files():
    return list_blend_files()

# Update the Gradio interface for rendering a single frame
render_single_frame_interface = gr.Interface(
    fn=render_single_frame,
    inputs=[gr.File(label="Upload Blender File (.blend)")],
    outputs=[gr.Textbox(label="Render Status"), gr.File(label="Rendered Frame")],
    title="Render Single Frame"
)

def render_multiple_frames(blender_file, selected_file_name, start_frame, end_frame):
    workspace_dir = '/workspace'
    os.makedirs(workspace_dir, exist_ok=True)

    # Generate a base name for the project folder
    if selected_file_name:
        # Use the name of the file selected from the dropdown
        base_name = os.path.splitext(selected_file_name)[0]
    elif blender_file is not None:
        # Use a timestamp for uploaded files
        timestamp = int(time.time())
        base_name = f"uploaded_blend_{timestamp}"
        blend_file_path = os.path.join(workspace_dir, base_name + ".blend")
        with open(blend_file_path, 'wb') as file:
            file.write(blender_file)
    else:
        return "No file provided.", None

    # Create a project folder with a concise name
    project_folder_name = f"{base_name}_frames_{start_frame}_to_{end_frame}"
    project_folder_path = os.path.join(workspace_dir, project_folder_name)
    os.makedirs(project_folder_path, exist_ok=True)

    output_file_base_path = os.path.join(project_folder_path, "frame")
    output_file_path = output_file_base_path + "_####.png"

    command = [
        "./blender/blender", "-P", "./blender/setgpu.py", "-b", blend_file_path,
        "-o", output_file_path, "-s", str(start_frame), "-e", str(end_frame), "-a"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        blender_logs = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        return f"Rendered frames {start_frame} to {end_frame} in '{project_folder_name}'.", blender_logs
    except subprocess.CalledProcessError as e:
        return "An error occurred: " + e.stderr.decode(), f"Error logs:\n{e.stderr.decode()}"
    finally:
        # Clean up the uploaded file if it was used
        if blender_file is not None and os.path.exists(blend_file_path):
            os.remove(blend_file_path)

def list_project_folders():
    workspace_dir = '/workspace'
    blend_dir = os.path.join(workspace_dir, 'blend')
    project_folders = [d for d in glob.glob(os.path.join(workspace_dir, '*/')) if d != blend_dir]
    return [os.path.basename(os.path.dirname(d)) for d in project_folders]

def export_output(project_folder):
    workspace_dir = '/workspace'
    blend_dir = os.path.join(workspace_dir, 'blend')
    project_dir = os.path.join(workspace_dir, project_folder)

    # Ensure the selected project is valid and exists
    if not os.path.exists(project_dir) or project_dir == blend_dir:
        return "Selected project folder does not exist or is invalid.", None

    # Create an export directory outside of the project directory
    export_dir = os.path.join(workspace_dir, 'export')
    os.makedirs(export_dir, exist_ok=True)
    export_zip_path = os.path.join(export_dir, f"{project_folder}.zip")

    # Create the zip file
    shutil.make_archive(export_zip_path.replace('.zip', ''), 'zip', project_dir)

    # Return the path of the zip file
    return export_zip_path

# Create individual Gradio interfaces for each part
system_info_interface = gr.Interface(
    fn=get_system_info,
    inputs=[],
    outputs=[gr.Textbox(label="System Info"), gr.Textbox(label="GPU Info")],
    title="System Information"
)

blender_version_setup_interface = gr.Interface(
    fn=download_and_setup_blender,
    inputs=[
        gr.Dropdown(choices=list(dl_link.keys()), label="Select Blender Version"),
        gr.Checkbox(label="Wipe Current Blender Installation Before Setup")
    ],
    outputs=[gr.Text(label="Setup Status")],
    title="Blender Version Setup",
    description="Select a Blender version to download and setup. You can also choose to wipe the current installation before setting up a new version."
)

render_single_frame_interface = gr.Interface(
    fn=render_single_frame,
    inputs=[
        gr.File(label="Upload Blender File (.blend)", type="binary"),
        gr.Dropdown(label="Or Select a Blender File", choices=list_blend_files())
    ],
    outputs=[
        gr.Textbox(label="Render Status"), 
        gr.File(label="Rendered Frame"),
        gr.Textbox(label="Blender Logs", lines=10)
    ],
    title="Render Single Frame"
)

render_multiple_frames_interface = gr.Interface(
    fn=render_multiple_frames,
    inputs=[
        gr.File(label="Upload Blender File (.blend)", type="binary"),
        gr.Dropdown(label="Or Select a Blender File", choices=list_blend_files()),
        gr.Number(label="Start Frame", value=1),  # You can set default values if desired
        gr.Number(label="End Frame", value=250)   # Adjust the default end frame as needed
    ],
    outputs=[
        gr.Textbox(label="Render Status"), 
        gr.Textbox(label="Blender Logs", lines=10)
    ],
    title="Render Multiple Frames"
)

export_output_interface = gr.Interface(
    fn=export_output,
    inputs=[
        gr.Dropdown(label="Select Project Folder", choices=list_project_folders())
    ],
    outputs=gr.File(label="Download Zip"),
    title="Export Rendered Frames"
)

# Combine them into a single TabbedInterface
tabbed_interface = gr.TabbedInterface(
    [blender_version_setup_interface, render_single_frame_interface, render_multiple_frames_interface, export_output_interface, system_info_interface],
    ["Blender Download", "Render Single Frame", "Render Multiple Frames", "Export", "System Info"]
)

# Launch the tabbed interface
tabbed_interface.launch(server_name="0.0.0.0", server_port=7860)

