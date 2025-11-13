import config
import utils
from detector import ObjectDetector
from tracker import LoiteringTracker
from alert_manager import AlertManager
from video_processor import VideoProcessor
import visualizer # We import the module directly

def main():
    """
    Main function to initialize and run the loitering detection application.
    """
    # Set up the logger
    logger = utils.setup_logger()
    logger.info("===========================================")
    logger.info("Starting Loitering Detection System")
    logger.info("===========================================")
    
    try:
        # 1. Initialize all components
        logger.info("Initializing components...")
        detector = ObjectDetector()
        tracker = LoiteringTracker()
        alert_manager = AlertManager()
        
        # 2. Initialize the main video processor
        # We pass the visualizer function itself, not an object
        processor = VideoProcessor(
            detector=detector,
            tracker=tracker,
            alert_manager=alert_manager,
            visualizer_func=visualizer.draw_visualizations
        )
        
        # 3. Start the processing threads
        logger.info("Starting video processing...")
        processor.start() # Starts the reader thread
        
        # 4. Run the main inference loop (this is blocking)
        processor.run_inference()

    except IOError as e:
        logger.error(f"Video source error: {e}")
    except Exception as e:
        logger.error(f"An unhandled error occurred: {e}", exc_info=True)
    finally:
        # 5. Ensure cleanup runs on exit or error
        logger.info("Shutting down...")
        if 'processor' in locals():
            processor.cleanup()
        logger.info("System stopped.")

if __name__ == "__main__":
    main()
