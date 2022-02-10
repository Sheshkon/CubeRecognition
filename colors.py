import numpy as np


lower_white = np.array([0, 0, 100])
upper_white = np.array([179, 43, 255])

lower_yellow = np.array([28, 50, 0])
upper_yellow = np.array([42, 255, 255])

lower_orange = np.array([0, 100, 0])
upper_orange = np.array([21, 200, 255])

lower_green = np.array([45, 50, 0])
upper_green = np.array([85, 255, 255])

lower_blue = np.array([95, 180, 0])
upper_blue = np.array([130, 255, 255])

# lower_red = np.array([156, 234, 0])
# upper_red = np.array([179, 255, 255])

lower_red1 = np.array([155, 150, 0])
upper_red1 = np.array([179, 255, 255])

lower_red2 = np.array([0, 200, 0])
upper_red2 = np.array([5, 255, 255])


pieces_colors = {
    1: 'W',
    2: 'R',
    3: 'G',
    4: 'Y',
    5: 'O',
    6: 'B'
}

rgb_colors = {
    1: (255, 255, 255),
    2: (0, 0, 255),
    3: (0, 255, 0),
    4: (0, 255, 255),
    5: (0, 140, 255),
    6: (255, 0, 0)
}

kociemba_colors = {
    1: 'U',
    2: 'R',
    3: 'F',
    4: 'D',
    5: 'L',
    6: 'B'
}

