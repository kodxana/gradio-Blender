# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y libxi6 libgconf-2-4 \
    && apt-get install -y libfontconfig1 libxrender1 \
    && apt-get install -y libboost-all-dev \
    && apt-get install -y libgl1-mesa-dev \
    && apt-get install -y libglu1-mesa libsm-dev libxkbcommon-x11-dev \
    && apt-get install -y ffmpeg  # Install ffmpeg

# Install Gradio
RUN pip install gradio psutil requests

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run blender_gradio_app.py when the container launches
CMD ["python", "./blender_gradio_app.py"]
