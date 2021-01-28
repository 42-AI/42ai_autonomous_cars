import os

# where the pictures + labels are saved by the Sim
logs_dir = "logs"
# threads to use to save images
max_threads = 16

# select track
track = "generated_track" # "roboracingleague_1" , "generated_track" , "generated_road" , "warehouse" , ...

# Training settings
val_split = 0.3
training_batch_size = 32
training_epochs = 50

# Data settings
seq_len = 8

image_width = 160
image_height = 120
image_depth = 1

bin_thresh = 230

crop_top = 0

# Car settings
fov = 150

cam_x = 0.0
cam_y = 0.4#1.0
cam_z = 2.8#3.8
cam_angle = 80

#angle_lims = [-0.8, -0.4, -0.2, -0.05, 0.05, 0.2, 0.4, 0.8]
#angle_idx = [-1.0, -0.8, -0.4, -0.2, 0.0, 0.2, 0.4, 0.8, 1.0]
angle_lims = [-0.5, -0.1, 0.1, 0.5]
angle_idx = [-1.0, -0.5, 0.0, 0.5, 1.0]

speed_lims = [0.0, 0.5]
speed_idx = [-0.5, 0.5, 1.0]

steering_out_scale = 1.0
throttle_out_scale = 0.75

min_speed = 9.0
