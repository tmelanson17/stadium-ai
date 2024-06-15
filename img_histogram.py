import cv2
import numpy as np

def histogram(img, axis=0):
    return cv2.calcHist([img],[axis],None,[256],[0,256]) 

def find_threshold(hist, threshold):
    total = np.sum(hist)
    cum = np.cumsum(hist)
    return np.argmax(cum > total*threshold)

if __name__ == "__main__":
    img = cv2.imread("data/example_battle.png")
    #blue_box = img[54:218, 82:370]
    blue_box = img[19:71, 97:189]
    hist = histogram(img)
    limit = int(find_threshold(hist), 0.75)
    red_limit = int(find_threshold(histogram(img, 2), 0.5))
    green_limit = int(find_threshold(histogram(img, 1), 0.5))
    print(limit)
    print(red_limit)
    print(green_limit)
    from matplotlib import pyplot as plt
    plt.plot(histogram(img, 2), 'r+')
    plt.plot(histogram(img, 1), 'g+')
    plt.plot(histogram(img, 0), 'b+')
    plt.plot(histogram(blue_box, 2), 'ro')
    plt.plot(histogram(blue_box, 1), 'go')
    plt.plot(histogram(blue_box, 0), 'bo')
    plt.legend()

    plt.show()
    cv2.imshow("Matrix", cv2.inRange(img, (limit, 0, 0), (255, red_limit, green_limit)))
    cv2.waitKey(0)
