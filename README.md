# ATM Pulse Designer

Used to simulate ATM pulses given input parameters and generate IQ files to use on devices.

This includes both a GUI and a jupyter notebook that can be used to visualize the pulses and save the data. The GUI includes live updating so you can get a general idea of the pulse shape as the simulation runs but is generally a bit buggier so if the pulse is especially long or has a very high maximum frequency is can be more stable but slower to use the notebook.

## Install:

Assuming you are in a terminal window that is in the root directory of this project:

### uv

Either run:

``` uv sync ```

if using uv (reccomended) to make the virtual environment. Then either open the ATMPulseTest.ipynb notebook or to use the gui run:

``` uv run ATMPulseDesigner.py ```

### pip

Otherwise create a venv with:

``` python -m venv ./.venv ```

Then activate the venv with:

``` ./.venv/Scripts/activate```

(This will be different on different consoles so if it does not work then just look it up I guess)

Then finally run:

``` pip install -r ./requirements.txt```

Then for the gui run:

``` python ATMPulseDesigner.py ```

or just open and use the notebook with the virtual environment that was just made.

## Pulse Design

These are some general guidelines for how each parameter can be changed to adapt the output. Some of these are more defined than others. 

With this in mind a generally good work flow is to start with deciding what you want out of the final pulse in respect to: pulse duration, sensivity, range, and tolerance/visibility. Once you have a general idea for these then set the corresponding parameters and play with the rest to try and achieve a response you are happy with.

### Pulse Time
Set depending mostly on how long you want the pulse to take. A longer pulse time will get better sensivity but settings it too long could cause there to be too much noise during the pulse and thus cause distortion. (Distortion will not be visible in the simulation so as a general rule of thumb stay below T2 Rabi time)

### Fall Time
This should be as long as you can make it without shortening the rise time and constant time so much that there is a lot of ripple/distortion in the response. The longer this is generally the better sensivity you can achieve by lowering the falling gradient.

### Rise Time
Should usually be half the Pulse Time - Fall Time. This can be played with to allow for longer fall time but giving enough time for the first 2 sections of the pulse will cause ripples in the response.

### Max Amplitude
Should probably be set to the measured Rabi Frequency. 

> [!IMPORTANT]
> This value will only change the simulation and not the waveform data that is saved. The waveform data is normalized to have a maximum of 1 and then should be set in qua or whatever code you use to be run at the same amplitude that was used to determine the Rabi frequency. There may also be some merit to running some experiments to look at the pulse response at different amplitudes when used on real devices.

### Max Frequency
This should be set to the detuning range you want (so if you want the pulse to detect a detuning range of 2MHz then this can be set to 2MHz)

> [!IMPORANT]
> Setting this too high can cause the simulation to take quite a while to run (The time steps must be dropped to prevent distortion due to the Nyquist frequency being too high)

### Rise Gradient
This accepts values between 0 and 1 exclusive with the closer to 1 having a steeper sloper and closer to 0 going to the smallest slope.

This values should be played with to try and minimize the ripple in the response. From what I have seen so far longer pulses this can be higher (0.95) and shorter pulses like this to be smaller (0.2) but we have not looked into this much.

### Fall Gradient
This also accepts values between 0 and 1 exclusive with the closer to 1 having a steeper sloper and closer to 0 going to the smallest slope.

This should be set as low as possible until the sensitivity starts to get worse again. The longer the pulse time the smaller this can be set and the better the sensitivity.

### Other

If you would like a more in depth explaination of the dynamics of the pulse and how some of the parameters affect the response feel free to message me.
