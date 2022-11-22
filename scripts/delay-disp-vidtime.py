import json, math

fpath = input("Path to data file: ")
offset = int(input("Video second offset: "))

DISP_THRESHOLD = 0.1
DELAY_THRESHOLD = 1.0

# Returns distance between points
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

objects = []
canvas = {}
with open(fpath) as fp:
    data = json.load(fp)
    objects = data['objects']
    canvas = data['canvas']
fps = canvas['fps']
units = canvas['units']

delays = []
disps = []
vid_times = []

x = objects[0]['X']
y = objects[0]['Y']

d = 1
for i in range(len(x) - 1):
    disp = dist(x[i], y[i], x[i + 1], y[i + 1])
    if disp < DISP_THRESHOLD:
        d += 1
    else:
        if d >= int(DELAY_THRESHOLD * fps):
            delays.append(d)
            disps.append(disp)
            vid_times.append(offset + (i / fps))
            d = 1

delays = [int(d / fps) for d in delays]

with open("delay-disp-vidtime-output.csv", "a") as fp:
    for i in range(len(delays)):
        fp.write(f'{delays[i]},{disps[i]},{vid_times[i]}\n')