import cv2
import os
import numpy as np
from io import BytesIO

#def trim_image(image_bytes: bytes) -> bytes:
def trim_image(image_folder, image_file) :
    """Trim the coffee cup image using an ellipse and triangle mask."""
    # Convert bytes to numpy array
    #img_array = np.frombuffer(image_bytes, np.uint8)
    #img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    #img_height, img_width, _ = img.shape

    # Create ellipse mask
    #Y, X = np.ogrid[:img_height, :img_width]
    #ellipse_mask = (((X - img_width / 2) ** 2) / (img_width / 2) ** 2 +
    #                ((Y - img_height / 2) ** 2) / (img_height / 2) ** 2) <= 1

    # Create triangle mask
    #triangle_pts = np.array([[0, img_height], [img_width, img_height], [img_width // 2, 0]])
    #triangle_mask = np.zeros((img_height, img_width), dtype=np.uint8)
    #cv2.fillPoly(triangle_mask, [triangle_pts], 1)

    # Combine masks
    #combined_mask = np.logical_and(ellipse_mask, triangle_mask)
    #if not np.any(combined_mask):
    #    raise ValueError("Combined mask is empty")

    # Apply mask and set background to average color
    #masked_pixels = img[combined_mask]
    #avg_color = np.mean(masked_pixels, axis=0).astype(np.uint8)
    #img2 = img.copy()
    #for c in range(3):
    #    img2[:, :, c][~combined_mask] = avg_color[c]

    # Convert back to bytes
    #_, buffer = cv2.imencode(".png", img2)
    #return buffer.tobytes()
    image_path = os.path.join(image_folder, image_file)
    #output_folder = os.path.join(image_path, 'TrimmedImages')
    #os.makedirs(output_folder, exist_ok=True)
    img = cv2.imread(image_path)
    img_height, img_width, _ = img.shape
    
    # Create an ellipse mask
    Y, X = np.ogrid[:img_height, :img_width]
    ellipse_mask = (((X - img_width / 2) ** 2) / (img_width / 2) ** 2 +
                    ((Y - img_height / 2) ** 2) / (img_height / 2) ** 2) <= 1
    
    # Create a triangle mask
    triangle_pts = np.array([[0, img_height], [img_width, img_height], [img_width // 2, 0]])
    triangle_mask = np.zeros((img_height, img_width), dtype=np.uint8)
    cv2.fillPoly(triangle_mask, [triangle_pts], 1)
    
    # Combine masks
    combined_mask = np.logical_and(ellipse_mask, triangle_mask)
    
    if not np.any(combined_mask):
        print(f'Warning: Combined mask is empty for {image_file}. Skipping...')
        #continue
    
    # Apply the mask
    masked_region = np.zeros_like(img)
    for c in range(3):
        channel_data = img[:, :, c]
        channel_data[~combined_mask] = 0
        masked_region[:, :, c] = channel_data
    
    # Calculate average color within the mask
    masked_pixels = img[combined_mask]
    avg_color = np.mean(masked_pixels, axis=0).astype(np.uint8)
    
    # Apply background color
    img2 = img.copy()
    for c in range(3):
        img2[:, :, c][~combined_mask] = avg_color[c]
    
    # Save trimmed image
    trimmed_image_path = os.path.join(image_folder, f'Trimmed_{os.path.splitext(image_file)[0]}.png')
    cv2.imwrite(trimmed_image_path, img2)
    success, buffer = cv2.imencode(".png", img2)
    if not success:
        raise ValueError("Image encoding failed")
    return trimmed_image_path

    
    