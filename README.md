# Download dataset
```bash
bash download.sh
```
This script will download the [SciVis mantle convection data](https://scivis2021.netlify.app/data) under the directory `DATA_DIR`.

# Preprocess
```bash
cd mantle
python3 data.py
```

# How to run
```bash
python3 main.py
```

## Flags
- `-d`, `--data`: The directory to all sphericalxxx.nc files. Default is 'data'
- `-r`, `--resolution`: This determines the resolution at which to voxelize the data. The program run faster the lower the resolution is. Default value is 100
- `-v`: This determines which mode to run the program. There are three choices: `ss` (scalar field vs scalar field), `sv` (scalar field vs vector field), and `vv` (vector field vs vector field).

## Example
```bash
python3 main.py -f velocity -r 100 -v ss
python3 main.py -f velocity -r 20 -v vv
python3 main.py -f velocity -r 20 -v sv
```

