import base64
import cv2
import numpy as np

# Load the image using OpenCV
image = cv2.imread("326-200x200.jpg")

# Encode the image to base64
_, image_bytes = cv2.imencode(".jpg", image)
image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# Print the base64 string (optional)
print(image_base64)

# Decode the base64 string back to an image
image_bytes_decoded = base64.b64decode(image_base64)
image_decoded = cv2.imdecode(np.frombuffer(image_bytes_decoded, np.uint8), cv2.IMREAD_COLOR)

# Verify if the decoded image is the same as the original
if (image_decoded == image).all():
    print("Image serialized and deserialized successfully!")

# Display the decoded image (optional, requires a GUI environment)
cv2.imshow("Decoded Image", image_decoded)
cv2.waitKey(0)
cv2.destroyAllWindows()