"""
Centroid-based person ID tracker
"""
import numpy as np
from scipy.spatial import distance as dist


class PersonTracker:
    def __init__(self, max_disappeared=30):
        self.next_id = 0
        self.objects = {}  # id -> centroid
        self.disappeared = {}  # id -> frame count
        self.max_disappeared = max_disappeared
    
    def register(self, centroid):
        """Register new person with unique ID"""
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1
        return self.next_id - 1
    
    def deregister(self, object_id):
        """Remove person from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, face_boxes):
        """
        Update tracker with new face detections
        Returns: dict of {id: centroid}
        """
        if len(face_boxes) == 0:
            # Mark all as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects
        
        # Calculate centroids
        input_centroids = np.zeros((len(face_boxes), 2), dtype="int")
        for i, (x, y, w, h) in enumerate(face_boxes):
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            input_centroids[i] = (cx, cy)
        
        # If no tracked objects, register all
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            # Match existing objects to new centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Compute distance matrix
            D = dist.cdist(np.array(object_centroids), input_centroids)
            
            # Find minimum distance matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Update existing object
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Check for disappeared objects
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            # Register new objects
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            for col in unused_cols:
                self.register(input_centroids[col])
        
        return self.objects
    
    def get_id_for_box(self, box):
        """Get person ID for given bounding box"""
        cx = int(box[0] + box[2] / 2.0)
        cy = int(box[1] + box[3] / 2.0)
        centroid = (cx, cy)
        
        # Find closest tracked object
        min_dist = float('inf')
        matched_id = None
        
        for object_id, obj_centroid in self.objects.items():
            d = dist.euclidean(centroid, obj_centroid)
            if d < min_dist:
                min_dist = d
                matched_id = object_id
        
        return matched_id if min_dist < 100 else None
