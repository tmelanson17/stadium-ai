import cv2

for i in range(10):
    print(f"Iteration {i}")
    img = cv2.imread(f"{i}.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cv2.imwrite(f"processed_{i}.jpg", img)
