#! python
import numpy as np
from random import random
from matplotlib import pyplot as plt
from matplotlib import rcParams as rcp

sizes = [11.139, 11.423, 10.125, 10.702, 10.552, 11.186, 10.040, 11.372, 9.017, 9.378, 9.804, 9.885, 11.185, 10.490, 10.952, 12.639, 11.409, 11.437, 12.266, 12.835, 10.950, 11.574, 10.848, 11.154, 9.546]
print(len(sizes))

#color = ((random() * 0.5) + 0.5, (random() * 0.5) + 0.5, (random() * 0.5) + 0.5)
color = (0.56078, 0.66274, 0.6)

rcp.update({'font.size': 30})
plt.hist(
    sizes, 
    edgecolor="black", 
    color=color, 
    density=True
)
plt.xlabel("Diameter (mm)")
plt.ylabel("P(diameter)")
plt.tight_layout()
plt.show()