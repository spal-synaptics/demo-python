# AI Demo with Python
This project uses Python3.10 to demo inference on a video input on the Synaptics Astra SL1680 board.
> [!NOTE]
> The firmware version on the SL1680 board must be >=1.0.0

## Running demo
Once you have the repository, there's two ways to run the demo:
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
The repository should now be cloned in a folder called `demo-python-main` and you can run the demo with `python3 main.py`.

#### 2. Directly run `demo-python.pyz`
Copy and run `demo-python.pyz` on the board:
```
curl -L -O https://raw.githubusercontent.com/spal-synaptics/demo-python/main/demo-python.pyz
python3 demo-python.pyz
```
This is a simpler approach recommended for users who don't wish to modify the demo itself.

### Run options
The demo can be run without any additional input arguments by doing `python3 demo-python.pyz` or `python3 main.py`.
The script will interactively ask for necessary information such as the video input and inference model details.


Alternatively, you can run with input arguments:
```
python3 demo-python.pyz \
-i <input source> \
-t <input type> \
-d <input dimensions> \
--inf_model <inference model> \
--inf_dims <model input size>
```
Use `python3 main.py --help` or `python3 demo-python.pyz --help` to get a list of available input arguments. The script will ask for any necessary information that is not provided via the input arguments.
