> python main.py
Flags:
-d, --data: The directory to all sphericalxxx.nc files. Default is 'data'
-f, --field: Which data field to visualize. Default is 'temperature'. Options are 'temperature', 'conductivity', 'anomaly', 'expansivity', 'velocity'
-r, --resolution: Resolution at which to voxelize the data. Lower is faster, higher is higher definition. Default is 100
--color_by_vector: When this flag is included, colors the velocity glyphs by their vector orientation rather than magnitude.
[ NOT IMPLEMENTED ] --camera: The path to the camera file storing the starting camera position.
