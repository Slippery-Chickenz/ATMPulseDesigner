# ATM Pulse Designer

(This is still kinda rough so expect at least the gui to be a bit slow/buggy)

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
