import cv2

def downsample_image():
    img = cv2.imread('capture/captured_image.jpg')
    if img is None:
        print("Image not found or path is incorrect!")
        return None
    small = cv2.pyrDown(img)
    cv2.imwrite('capture/downsample.jpg', small)
    print("Downsampled image saved as capture/downsample.jpg")
    return 'capture/downsample.jpg'