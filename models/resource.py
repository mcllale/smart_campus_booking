"""
models/resource.py
Simple data class representing a bookable campus resource (computer lab,
projector, seminar room, etc.). Most queries return raw tuples for speed;
this class exists so the GUI layer can work with a friendlier object shape
where that's convenient.
"""


class Resource:
    def __init__(self, resource_id, campus, name, resource_type):
        self.resource_id = resource_id
        self.campus = campus
        self.name = name
        self.resource_type = resource_type

    def __str__(self):
        return f"{self.resource_id} - {self.name} ({self.resource_type})"

    @staticmethod
    def from_campus_row(campus_name, row):
        """row: (resource_id, name, resource_type), as returned by queries
        that already filter by a specific campus."""
        resource_id, name, resource_type = row
        return Resource(resource_id, campus_name, name, resource_type)
