import cv2
import config

def draw_visualizations(frame, results, loitering_data):
    """
    Draws bounding boxes, track IDs, and loitering timers on the frame.

    Args:
        frame: The video frame to draw on.
        results: The YOLO results object.
        loitering_data (dict): The status data from LoiteringTracker.

    Returns:
        The annotated video frame.
    """
    annotated_frame = frame.copy()

    # Check if tracking IDs are available
    if results.boxes.id is None:
        return annotated_frame # Return original frame if no tracks

    # Extract data from the results object
    boxes = results.boxes.xyxy.cpu().numpy().astype(int)
    track_ids = results.boxes.id.cpu().numpy().astype(int)

    # Iterate over each tracked object
    for box, track_id in zip(boxes, track_ids):
        x1, y1, x2, y2 = box
        
        # Get loitering status for this track
        status_info = loitering_data.get(track_id)
        
        if status_info:
            elapsed_time = status_info['elapsed']
            status = status_info['status']
            
            # Determine color based on status
            if status == "alert":
                color = config.COLOR_RED
                label = f"ID: {track_id} (LOITERING: {elapsed_time:.1f}s)"
            elif status == "warn":
                color = config.COLOR_ORANGE
                label = f"ID: {track_id} ({elapsed_time:.1f}s)"
            else:
                color = config.COLOR_GREEN
                label = f"ID: {track_id} ({elapsed_time:.1f}s)"
        
            # Draw the bounding box
            cv2.rectangle(
                annotated_frame, 
                (x1, y1), 
                (x2, y2), 
                color, 
                2
            )
            
            # Draw the label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(
                annotated_frame, 
                (x1, y1 - 20), 
                (x1 + w, y1), 
                color, 
                -1
            )
            
            # Draw the label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255), # White text
                2
            )
            
    return annotated_frame
