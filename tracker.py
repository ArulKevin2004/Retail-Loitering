import time
import config
from utils import logger

class LoiteringTracker:
    """
    Manages the loitering time for each tracked person.
    """
    def __init__(self):
        # Dictionary to store the start time for each track_id
        # {track_id: start_time}
        self.track_timers = {}
        
        # Set to store track_ids that have already triggered an alert
        # This prevents sending duplicate alerts for the same person
        self.alerted_ids = set()

    def update(self, current_track_ids):
        """
        Updates the timers for all tracked individuals.

        Args:
            current_track_ids (list): A list of track_ids currently
                                     visible in the frame.
        
        Returns:
            dict: A dictionary mapping track_id to its loitering status.
                  {track_id: {'elapsed': float, 'status': str}}
        """
        current_time = time.time()
        seen_ids = set(current_track_ids)
        status_data = {}

        # 1. Handle disappeared tracks
        # Find tracks that were present but are now gone
        disappeared_ids = set(self.track_timers.keys()) - seen_ids
        for track_id in disappeared_ids:
            logger.info(f"Track ID {track_id} disappeared.")
            del self.track_timers[track_id]
            self.alerted_ids.discard(track_id) # Remove from alerted set if they leave

        # 2. Update existing tracks and add new ones
        for track_id in current_track_ids:
            # This is a new track
            if track_id not in self.track_timers:
                logger.info(f"New Track ID {track_id} appeared.")
                self.track_timers[track_id] = current_time
                elapsed_time = 0
                status = "new"
            else:
                # This is an existing track
                elapsed_time = current_time - self.track_timers[track_id]
                
                # Determine status
                if elapsed_time > config.LOITERING_THRESHOLD_SEC:
                    status = "alert"
                elif elapsed_time > (config.LOITERING_THRESHOLD_SEC * config.WARN_THRESHOLD_PERCENT):
                    status = "warn"
                else:
                    status = "tracking"
            
            status_data[track_id] = {
                'elapsed': elapsed_time,
                'status': status
            }
        
        return status_data

    def has_been_alerted(self, track_id):
        """Checks if an alert has already been sent for this track_id."""
        return track_id in self.alerted_ids

    def mark_alerted(self, track_id):
        """Marks a track_id as having been alerted."""
        logger.info(f"Marking Track ID {track_id} as alerted.")
        self.alerted_ids.add(track_id)
