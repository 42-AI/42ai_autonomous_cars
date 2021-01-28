# Get Data :

### 1 - Get the simulator accordingly to your system: https://github.com/tawnkramer/gym-donkeycar/releases

### 2 - Install dependencies:
```
pip install -r requirements.txt
```

### 2 - Check the config.py file, edit it if needed (track, "logs" folder: where the data will be saved, camera, car settings...)

### 3 - Plug in your Gamepad

### 4 - Start the simulator, stay on the home page, the script will select the track from config

### 5 - Start the "man_client.py" script, check there is no error, and drive !
```
python man_client.py
```

### 6 - Grab you images and labels from the "logs" folder (or other place you selected), time to Crunch Data !

# Train

### Those are experimentation's notebooks so expect errors, maybe don't run every cell... :

```
jupyter notebook
```

Donkey_Sim_Notebook: single images => categorical output
Donkey_Sim_Multi_Notebook: images sequences with Conv3D or ConvLSTM2D => categorical output
Donkey_Sim_Notebook_mse: single images => linear output

# Autonomous Drive

### To be honest, I haven't tryed those since a while, may work thought... :

Corresponding scripts to run trained model on simulator

```
python choosen_script.py --model my_model
```

sup_client.py
sup_client_multi.py
sup_client_mse.py