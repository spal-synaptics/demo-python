# AI Demo with Python
This project uses Python3.10 to demo inference on a video input on the Synaptics Astra SL1680 board.
> [!IMPORTANT]
> The firmware version on the SL1680 board must be >=1.0.0

## Running demos
There's two ways of running the demos:
#### 1. Clone repository and run `main.py`
This method is recommended if you wish to:
- Extend the functionality of the demo by modifying its components, or
- Customize the demo to suit a specific use-case.

Note that `git` may not be supported on your firmware. If your board doesn't support `git`, do the following:
```bash
curl -L -O https://github.com/spal-synaptics/demo-python/archive/main.zip
unzip main.zip
rm main.zip
```
The repository should now be cloned in a folder called `demo-python-main`. You can now run `python3 demo.py` or any of the specific [examples](examples).

#### 2. Directly run .pyz executables
The [exec](exec) folder contains single file executable zip archives (`.pyz`) that can be run on the baord as-is. To copy an executable to the board, replace `<demo>` with the actual executable filename in this command:
```
curl -L -O https://raw.githubusercontent.com/spal-synaptics/demo-python/main/exec/<demo>.pyz
python3 <demo>.pyz
```
This is a simpler approach recommended for users who don't wish to modify the demo itself.

### Run options
> [!TIP]
> `.py` and `.pyz` files are interchangeable for this section
#### Main demo
`demo.py` is a generic demo that can be used for any input source and has several customization options. The demo can be run without any additional input arguments by doing `python3 demo.py`.
The script will interactively ask for necessary information such as the video input and inference model details.


Alternatively, you can run with input arguments:
```
python3 demo-python.pyz \
-i <input source> \
-t <input type> \
-d <input dimensions> \
--model <inference model>
```
Use `python3 demo.py --help` to get a list of available input arguments. The script will ask for any necessary information that is not provided via the input arguments.

#### Specific examples
The [examples](examples) folder contains input-specific demos. These are less customizable but easier to run, and can serve as quickstart demos to test out an input source or AI model.
The default parameters for an example can be directly modified in its Python script, or overridden via input arguments similar to `demo.py`. To run an example do `python3 <example>.py`. 
