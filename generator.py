import itertools
import json


class City:
    def __init__(self):
        self.json = {
            "type": "CityJSON",
            "version": "2.0",
            "extensions": {},
            "transform": {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]},
            "metadata": {},
            "CityObjects": {},
            "vertices": [],
            "appearance": {},
            "geometry-templates": {"templates": [], "vertices-templates": []},
        }
        self.templates: dict[str, int] = {}
        self._cityobject_counter = itertools.count()

    def new_cityobject_id(self):
        return f"id_{next(self._cityobject_counter)}"

    def to_cityjson(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.json, f)

    @property
    def cube_template(self) -> int:
        # If we've called it before, we don't have to add it again
        if (template_id := self.templates.get("cube")) is not None:
            return template_id

        # If this is the first call, store the id for later reference
        n = len(self.json["geometry-templates"]["templates"])
        self.templates["cube"] = n

        # Insert the vertices
        self.json["geometry-templates"]["vertices-templates"].extend(
            [
                [0, 0, 0],  # bottom-south-west
                [1, 0, 0],  # bottom-south-east
                [1, 1, 0],  # bottom-north-east
                [0, 1, 0],  # bottom-north-west
                [0, 0, 1],  # top-south-west
                [1, 0, 1],  # top-south-east
                [1, 1, 1],  # top-north-east
                [0, 1, 1],  # top-north-west
            ]
        )

        # Insert the geometry template with correct offset for the vertices
        self.json["geometry-templates"]["templates"].append(
            {
                "type": "Solid",
                "lod": "1",
                "boundaries": [
                    [
                        [[n + 0, n + 1, n + 2, n + 3]],  # bottom
                        [[n + 4, n + 5, n + 1, n + 0]],  # south
                        [[n + 5, n + 6, n + 2, n + 1]],  # east
                        [[n + 6, n + 7, n + 3, n + 2]],  # north
                        [[n + 7, n + 4, n + 0, n + 3]],  # west
                        [[n + 7, n + 6, n + 5, n + 4]],  # top
                    ]
                ],
            }
        )

        return n

    def add_vertex(self, x: int, y: int, z: int = 0):
        self.json["vertices"].append([x, y, z])

        return self

    def add_vertices(self, x: list[int], y: list[int], z: list[int] = None):
        if z is None:
            for _x, _y in zip(x, y):
                self.add_vertex(_x, _y)
        else:
            for _x, _y, _z in zip(x, y, z):
                self.add_vertex(_x, _y, _z)

        return self

    def add_cube(self, location_id):
        template_id = self.cube_template
        cityobject_id = self.new_cityobject_id()

        object = {
            "type": "GenericCityObject",
            "geometry": [
                {
                    "type": "GeometryInstance",
                    "template": template_id,
                    "boundaries": [location_id],
                    "transformationMatrix": [
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        1,
                    ],
                }
            ],
        }

        self.json["CityObjects"][cityobject_id] = object
        return self


if __name__ == "__main__":
    City().add_vertices([0, 0], [2, 0], [0, 0]).add_cube(0).add_cube(1).to_cityjson(
        "test.city.json"
    )
