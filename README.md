# AI Demo with Python
This project uses Python3.10 to demo inference on a video input on the Synaptics Astra SL1680 board.
> [!NOTE]
> The firmware version on the SL1680 board must be >=1.0.0

## Running demo
There are two ways to run this demo. 
#### Clone repository and run `__main__.py`
This method is recommended if you wish to:
1. Extend the functionality of the demo by modifying its components.
2. Customize the demo to suit a specific use-case.

Note that `git` isn't yet natively supported on the SL1680 firmware, so this approach involves cloning the repo to a separate machine and then transferring over to the board with `adb push` or `scp`.

#### Directly run `demo-python.pyz`
Copy `demo-python.pyz` to the board and run with `python3 demo-python.pyz`. This is an easier approach and recommended for users who don't wish to modify the demo itself.

### Run options
The demo can be run without any additional input arguments: `python3 demo-python.pyz` or `python3 __main__.py`.
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
Use `python demo-python.pyz --help` to get a list of available input arguments. The script will ask for any necessary information that is not provided via the input arguments.
