#!/usr/bin/env python3
#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import sys
import numpy as np
from jetson_inference import poseNet
from jetson_utils import videoSource, videoOutput

# Hard-coded path for the standard video
STANDARD_VIDEO_PATH = "/home/nvidia/myproject/tiger.mp4"  # Replace this with the actual path

# Prompt user for input video path
input_video_path = input("Please enter the path to the input video: ")

# Define a default output video path
DEFAULT_OUTPUT_VIDEO_PATH = "/home/nvidia/myproject/annotated_output.mp4"

# Load the pose estimation model
network = "resnet18-body"  # Default network
threshold = 0.15  # Default detection threshold
overlay = "links,keypoints"  # Default overlay flags
net = poseNet(network, sys.argv, threshold)

# Create video sources (input and standard)
input_video = videoSource(input_video_path, argv=sys.argv)
standard_video = videoSource(STANDARD_VIDEO_PATH, argv=sys.argv)

# Create a video output stream with the default path
output = videoOutput(DEFAULT_OUTPUT_VIDEO_PATH, argv=sys.argv)

# Function to compare two poses using Cosine Similarity
def compare_poses(pose1, pose2):
    keypoints1 = pose1.Keypoints
    keypoints2 = pose2.Keypoints
    
    vector1 = []
    vector2 = []
    
    for kp1, kp2 in zip(keypoints1, keypoints2):
        vector1.append(kp1.x)
        vector1.append(kp1.y)
        vector2.append(kp2.x)
        vector2.append(kp2.y)
    
    # Convert lists to numpy arrays
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    
    # Calculate cosine similarity
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    cosine_similarity = dot_product / (norm1 * norm2)
    
    return cosine_similarity

# Initialize total similarity and count
total_similarity = 0
pose_count = 0

# Process frames from both videos until EOS or the user exits
while True:
    # Capture the next frame from each video
    input_frame = input_video.Capture()
    standard_frame = standard_video.Capture()

    # Exit the loop if either video ends
    if input_frame is None or standard_frame is None:
        break

    # Check for rotation metadata and adjust frames accordingly
    if input_frame.width != standard_frame.width or input_frame.height != standard_frame.height:
        input_frame.Resize(standard_frame.width, standard_frame.height)

    # Perform pose estimation on both frames
    input_poses = net.Process(input_frame, overlay=overlay)
    standard_poses = net.Process(standard_frame, overlay=overlay)

    # Compare each pose in the input frame with the corresponding pose in the standard frame
    if len(input_poses) > 0 and len(standard_poses) > 0:
        for input_pose, standard_pose in zip(input_poses, standard_poses):
            similarity = compare_poses(standard_pose, input_pose)
            total_similarity += similarity
            pose_count += 1
            print(f"Pose similarity score (Cosine): {similarity:.2f}")

    # Render the input frame to the output video
    output.Render(input_frame)

    # Print out performance info
    net.PrintProfilerTimes()

    # Exit on input/output EOS
    if not input_video.IsStreaming() or not standard_video.IsStreaming() or not output.IsStreaming():
        break

# Calculate average similarity
if pose_count > 0:
    average_similarity = total_similarity / pose_count
    average_similarity_percentage = average_similarity * 100
    print(f"Average pose similarity (Cosine): {average_similarity:.2f}")
    print(f"Average pose similarity in percentage: {average_similarity_percentage:.2f}%")
else:
    print("No poses were detected in the videos.")
