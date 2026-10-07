import numpy as np
import cv2
import dxcam
import serial

# ser = serial.Serial("COM6",921600,timout=0)

light_w = 30
light_h = 18

cam = dxcam.create(output_color="BGR")
cam.start(target_fps=30)
cv2.namedWindow("window", cv2.WINDOW_NORMAL)
cv2.resizeWindow("window",384,216)

def normalize_color(color,coord,axis):
    if axis == "x":
        total = 9
    else:
        total = 15
    return color*coord*total

def strip(colors):
    arr = np.array(colors, dtype=np.uint8).reshape(1, len(colors), 3)
    return cv2.resize(arr, (len(colors) * 20, 40), interpolation=cv2.INTER_NEAREST)

def render(top, right, bottom, left):
    cv2.imshow("top",    strip(top))
    cv2.imshow("bottom", strip(bottom))
    cv2.imshow("left",   strip(left))
    cv2.imshow("right",  strip(right))

tau = 4.0

rows = np.arange(18)
top_dist    = rows[0:9]  
bottom_dist = 17 - rows[9:18]

cols = np.arange(30)
left_dist  = cols[0:15]
right_dist = 29 - cols[15:30]

def weights_from_dist(dist):
    w = np.exp(-dist / tau)
    return w / w.sum()    

while 1:
    top = [[0,0,0] for _ in range(30)]
    bottom = [[0,0,0] for _ in range(30)]
    left = [[0,0,0] for _ in range(18)]
    right = [[0,0,0] for _ in range(18)]
    frame = cam.get_latest_frame()

    if frame is None:
        continue
    downscaled = cv2.resize(frame,(light_w,light_h),interpolation=cv2.INTER_AREA)

    w_top, w_bottom = weights_from_dist(top_dist), weights_from_dist(bottom_dist)
    w_left, w_right = weights_from_dist(left_dist), weights_from_dist(right_dist)

    top    = np.clip((downscaled[0:9, :, :]  * w_top[:, None, None]).sum(axis=0), 0, 255).astype(np.uint8)
    bottom = np.clip((downscaled[9:18, :, :] * w_bottom[:, None, None]).sum(axis=0), 0, 255).astype(np.uint8)
    left   = np.clip((downscaled[:, 0:15, :] * w_left[None, :, None]).sum(axis=1), 0, 255).astype(np.uint8)
    right  = np.clip((downscaled[:, 15:30, :]* w_right[None, :, None]).sum(axis=1), 0, 255).astype(np.uint8)

    allbgr = np.vstack([top,right,bottom,left])
    allrgb = allbgr[:,::-1]
    payload = allrgb.astype(np.uint8).tobytes()
    checksum = sum(payload) & 0xFF
    # ser.write(bytes([0xAA,0x55]) +payload+ bytes(checksum))
    
    render(top,right,bottom,left)
    cv2.waitKey(1)