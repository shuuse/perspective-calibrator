import cv2
import numpy as np
import os

class PerspectiveCalibrator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")
        print(f"Loaded image with shape: {self.image.shape}")
        self.points = []
        self.window_name = "Perspective Calibrator"
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append([x, y])
            # Draw the point
            cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
            
            # Draw lines between points as they're added
            if len(self.points) > 1:
                for i in range(len(self.points) - 1):
                    pt1 = tuple(self.points[i])
                    pt2 = tuple(self.points[i + 1])
                    cv2.line(self.image, pt1, pt2, (0, 255, 0), 2)
                
                # Close the shape if we have all 4 points
                if len(self.points) == 4:
                    cv2.line(self.image, tuple(self.points[3]), tuple(self.points[0]), (0, 255, 0), 2)
                    self.calculate_extended_points()
            
            cv2.imshow(self.window_name, self.image)
            print(f"Added point {len(self.points)}: [{x}, {y}]")
            
            if len(self.points) == 1:
                print("Now click top right point (same distance from camera)")
            elif len(self.points) == 2:
                print("Now click bottom right point")
            elif len(self.points) == 3:
                print("Now click bottom left point (same distance from camera as bottom right)")
    
    
    
    def preview_transform(self):
        if len(self.points) != 4:
            print("Need 4 points to preview transformation")
            return
            
        # Define target points for a reasonable preview size
        height = self.image.shape[0]
        width = int(height * 0.5)  # 2:1 aspect ratio for preview
        target_points = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype=np.float32)
        
        # Get transformation matrix
        source_points = self.source_points.astype(np.float32)
        matrix = cv2.getPerspectiveTransform(source_points, target_points)
        
        # Apply transformation
        warped = cv2.warpPerspective(
            self.image,
            matrix,
            (width, height)
        )
        
        # Show the preview
        cv2.imshow("Transformation Preview", warped)
        
    
    def calculate_extended_points(self):
        # Get the marked points
        top_left = np.array(self.points[0])
        top_right = np.array(self.points[1])
        bottom_right = np.array(self.points[2])
        bottom_left = np.array(self.points[3])
        
        # Calculate slopes of left and right lines
        left_slope = (bottom_left[1] - top_left[1]) / (bottom_left[0] - top_left[0])
        right_slope = (bottom_right[1] - top_right[1]) / (bottom_right[0] - top_right[0])
        
        # Calculate where these lines intersect y = image_height
        bottom_y = self.image.shape[0]
        
        # x = x1 + (y - y1)/slope
        left_x = top_left[0] + (bottom_y - top_left[1]) / left_slope
        right_x = top_right[0] + (bottom_y - top_right[1]) / right_slope
        
        # Store the complete set of points for SOURCE
        self.source_points = np.array([
            top_left,
            top_right,
            [right_x, bottom_y],
            [left_x, bottom_y]
        ])
        
        # Draw the extended lines
        temp_image = self.image.copy()
        
        # Draw original rectangle in green
        cv2.polylines(temp_image, [np.array(self.points)], True, (0, 255, 0), 2)
        
        # Draw extended lines in blue
        cv2.line(temp_image, tuple(top_left), (int(left_x), bottom_y), (255, 0, 0), 2)
        cv2.line(temp_image, tuple(top_right), (int(right_x), bottom_y), (255, 0, 0), 2)
        
        cv2.imshow(self.window_name, temp_image)
        
        print("\nExtended points calculated:")
        print(f"Bottom left intersection: [{int(left_x)}, {bottom_y}]")
        print(f"Bottom right intersection: [{int(right_x)}, {bottom_y}]")
    
    def calibrate(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        cv2.imshow(self.window_name, self.image)
        
        print("\nInstructions:")
        print("1. Click top left point")
        print("2. Press 'r' to reset if you make a mistake")
        print("3. Press 'p' to preview transformation")
        print("4. Press 's' to save when done")
        print("5. Press 'q' to quit\n")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('r'):
                self.image = cv2.imread(self.image_path)
                self.points = []
                cv2.imshow(self.window_name, self.image)
                print("Reset points")
                print("Click top left point")
            
            elif key == ord('s') and len(self.points) == 4:
                print("\nSOURCE points for your script:")
                print("SOURCE = np.array([")
                for point in self.source_points:
                    print(f"    [{int(point[0])}, {int(point[1])}],")
                print("])")
                np.save('source_points.npy', self.source_points)
                print("\nPoints saved to 'source_points.npy'")
            
            elif key == ord('p') and len(self.points) == 4:
                self.preview_transform()
            
            elif key == ord('q'):
                break
        
        cv2.destroyAllWindows()



def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", help="Path to video file")
    parser.add_argument("--image", help="Path to image file")
    args = parser.parse_args()
    
    try:
        if args.video:
            print(f"Opening video: {args.video}")
            cap = cv2.VideoCapture(args.video)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {args.video}")
            
            ret, frame = cap.read()
            if not ret:
                raise ValueError("Could not read frame from video")
            
            print("Successfully read first frame from video")
            first_frame_path = "first_frame.jpg"
            cv2.imwrite(first_frame_path, frame)
            cap.release()
            
            if not os.path.exists(first_frame_path):
                raise ValueError("Failed to save first frame")
            
            image_path = first_frame_path
            
        elif args.image:
            print(f"Using image: {args.image}")
            if not os.path.exists(args.image):
                raise ValueError(f"Image file does not exist: {args.image}")
            image_path = args.image
        else:
            raise ValueError("Please provide either --video or --image argument")
        
        calibrator = PerspectiveCalibrator(image_path)
        calibrator.calibrate()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()