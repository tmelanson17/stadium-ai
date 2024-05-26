import cv2
import numpy as np

def find_letter(base_img, letter_img):
	# filter2d ( src, ddepth, kernel)
	activations = cv2.filter2D(base_img, -1, letter_img)
	return activations

if __name__ == "__main__":
	base = cv2.imread("example_battle_p1_box.png", cv2.IMREAD_UNCHANGED)[:,:,2]
	# base = cv2.morphologyEx(base, cv2.MORPH_OPEN, np.ones([2,2]))
	base = cv2.erode(base, np.ones([2,2]), iterations=1)
	cv2.imwrite("example_battle_p1_box_enhanced.png", base)
	letter = cv2.imread("n.png", cv2.IMREAD_UNCHANGED)[:,:,-1].astype(float) / 255.
	letter = cv2.resize(letter, (9,14), cv2.INTER_CUBIC) # , fx=2, fy=2)
	#letter = cv2.erode(letter, np.ones([3,3]), iterations=1)

	cv2.imshow("Letter:", letter)
	letter /= np.sum(letter)
	base = base.astype(float) / 255.
	cv2.imshow("Base: ", base)
	print("Letter image size:", letter.shape)
	print("Base image size:", base.shape)
	output = find_letter(base, letter)
	idx = np.unravel_index(np.argmax(output, axis=None), output.shape)
	print(np.min(output), np.max(output))
	print("Location: ", idx)
	# output[output<0.6] = 0
	cv2.imshow("Activations: ", output*output)
	cv2.waitKey(0)
	
