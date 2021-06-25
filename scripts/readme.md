# Script Usage

## Preprocessing

#### perspective_transform.py

```
usage: perspective_transform.py [-h] [-d] path

Perspective transform image sequences using OpenCV

positional arguments:
  path         Path to folder with frames

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Show debug information
```

##### Notes:

- The script looks for all images ending in `.jpg`/`.jpeg`/`.bmp`/`.png` in the folder at the given path, tries to sort them naturally and assumes they are named "ImageXXXX". This image prefix ("Image") can be changed as a program constant.
- After running the script, you should click the four corners of the bounding box (in the order top left, bottom left, top right, bottom right), then hit "P" to process the images. If you mis-click the coordinates, you can hit "R" to reset them, and "Q" to exit the program at any time.

- Output images are scaled to the original image's width and height - at some point the bounding box dimensions will be properly calculated to minimize stretching here but shouldn't cause issues at even medium-low resolutions and higher.
- Output image scaling also does not retain aspect ratio between width and height - this is not a problem for tracking because usually real width and real height is specified, but once bounding box dimensions are calculated it should better retain aspect ratio.

#### preprocess.py

```
usage: preprocess.py [-h] [-nfx] [-d] path

Preprocess videos for tracking using OpenCV to modify frames and stitch into
video.

positional arguments:
  path          Path to image frames

optional arguments:
  -h, --help    show this help message and exit
  -nfx, --nofx  Disable filtering video, just dump raw frames
  -d, --debug   Show debug information
```

##### Notes:

- Reads all image files ending in `.jpg` or `.png` from the given folder, naturally sorts them (assuming they are prefixed with "Image" as in `ImageXXXX.jpg`), then applies the given filters and writes them to a video file in the same folder as the images, named `video.mp4`.
- Has a couple different filters commented out and tweaked, there's not much interaction with the script arguments here as it is usually set to reasonable settings and then left as-is.

## Tracking/Processing

#### opencv_track.py

```
usage: opencv_track.py [-h] [-rw REAL_WIDTH] [-rh REAL_HEIGHT] [-u UNITS] [-d]
                       path

Multi-object tracking using OpenCV contour detection, centroid calculation,
and tracking algorithms

positional arguments:
  path                  Path to video, ending in .avi or .mp4

optional arguments:
  -h, --help            show this help message and exit
  -rw REAL_WIDTH, --real-width REAL_WIDTH
                        Real width of canvas, defaults to image height
  -rh REAL_HEIGHT, --real-height REAL_HEIGHT
                        Real height of canvas, defaults to image height
  -u UNITS, --units UNITS
                        Units for canvas, defaults to 'pixels'
  -d, --debug           Show debug information
```

##### Notes:

- Writes position data to `pos_data.json`, in the same folder as the given video file.
- Currently, only set up to accept files with `.avi` and `.mp4` extensions.
- It is possible to provide a real width and not a real height, and vice versa, but as this has no practical use (and it is more user-friendly to specify them as separate arguments) it may cause unintended results (i.e., the x direction is scaled 0-30, but the y direction ends up scaled 0-4000).
- Couple running errors/limitations to be resolved with the tracking:
  - Does not handle object collisions well at the moment
  - Does not handle objects hitting the corner of the frame
- Currently just looks for the nearest object in the last frame when deciding what object corresponds with each detected object in the next frame - this will be replaced with a loss function to help when objects are close in the future.

#### trim_positions.py

```
usage: trim_positions.py [-h] [-ss SEEK] [-to TO] [-d] path

Trim position data from file, seeking to specific frame

positional arguments:
  path                  Path to position data file

optional arguments:
  -h, --help            show this help message and exit
  -ss SEEK, --seek SEEK
                        Seek to specific frame in position data file
  -to TO, --to TO       Retrieve position data until specific frame
  -d, --debug           Show debug information
```

##### Notes:

- Script takes a start and end position, then opens the given position data file, pulls out those positions, and writes to the same directory as the original file, saved as `pos_data_{start}_{end}.json` (i.e., `pos_data_1_200.json`).
- `-ss` and `-to` are both optional, if they aren't specified the "seek" is set to the first frame and the "to" is set to the last frame (giving you the same position data file as the input).

## Analyzing/Plotting

#### display_positions.py

```
usage: display_positions.py [-h] [-d] path

Display position from json position data files

positional arguments:
  path         Path to file containing position data

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Show debug information
```

##### Notes:

- Displays an animation of objects from the position data file, looping through frames until the user closes the window or hits "Q". After this, the program asks if you want to save the animation, and it will be saved in the same folder the program is run from, as `animation.mp4`.

#### display_msd.py

```
usage: display_msd.py [-h] [-d] path

Display mean-squared displacement (MSD) plots from position data files

positional arguments:
  path         Path to file containing position data

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Show debug information
```

##### Notes:

- Displays an MSD plot (scaled to log base 10 in both axes) for the given position data. Units are pulled from the units specified in the position data file. The plot is displayed until the user closes the window or hits "Q", after which the program asks if they want to save the plot, which is then saved to `figure.png` in the same folder the script is run from.

#### display_delay.py

```
usage: display_delay.py [-h] [-t THRESHOLD] [-o OBJECTS] [-b BIN_FACTOR] [-d]
                        path

Display probability distribution of delays between jumps from json position
data files

positional arguments:
  path                  Path to file containing position data

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold of activity, defaults to 0.1
  -o OBJECTS, --objects OBJECTS
                        Index of objects to calculate delays for, accepts
                        comma-separated list of indices
  -b BIN_FACTOR, --bin-factor BIN_FACTOR
                        Bins are set to show every value in input data, this
                        accepts a multiplier to increase or reduce that number
                        (defaults to 1)
  -d, --debug           Show debug information
```

##### Notes:

- Displays a delay distribution plot (histogram of delays between object movement). After the plot is displayed, the script waits until the window is closed or the user hits "Q". Then, the program asks if the user wants to save the plot, which ends up as `figure.png` in the same directory the script is run in.
- The threshold for what is considered movement defaults to 0.1 in whichever units the position data file specifies, and can be overridden using the threshold argument.
- The objects to track defaults to all objects in the position data file, but can be overridden by specifying a comma-separated list of object numbers (i.e., `--objects 1,3,4` or `-o 2`).
- The output plot defaults to setting the number of bins to the highest delay in the calculated delays, but using the bin factor argument that number can be modified. By specifying a bin factor of 0.5 with `--bin-factor 0.5` or `-b 0.5`, the number of bins is halved. By specifying a bin factor of 2.0 with `-b 2.0`, the number of bins is doubled.