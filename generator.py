import itertools
import json


def transformation_matrix(translation=(0, 0, 0), scaling=(1, 1, 1)):
    # fmt: off
    return [
        scaling[0], 0, 0, translation[0],
        0, scaling[1], 0, translation[1],
        0, 0, scaling[2], translation[2],
        0, 0, 0, 1,
    ]
    # fmt: on


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
            "appearance": {"materials": [], "textures": []},
            "geometry-templates": {"templates": [], "vertices-templates": []},
        }
        self.templates: dict[str, int] = {}
        self.materials: dict[str, int] = {}
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

        return len(self.json["vertices"]) - 1

    def add_template(
        self, template_id: int, x: int, y: int, z: int = 0, scaling=(1, 1, 1)
    ) -> str:
        location_id = self.add_vertex(x, y, z)
        cityobject_id = self.new_cityobject_id()

        object = {
            "type": "GenericCityObject",
            "geometry": [
                {
                    "type": "GeometryInstance",
                    "template": template_id,
                    "boundaries": [location_id],
                    "transformationMatrix": transformation_matrix(scaling=scaling),
                }
            ],
        }

        self.json["CityObjects"][cityobject_id] = object
        return cityobject_id

    def add_cube(self, x: int, y: int, z: int = 0, scaling=(1, 1, 1)) -> str:
        return self.add_template(self.cube_template, x, y, z, scaling=scaling)

    def add_material(self, name: str, color=[0.5, 0.5, 0.5]) -> str:
        """Add a material with `name` and `color` to appearences dict.

        color should be a list of rgb values between 0 and 1.
        """
        # If we've called it before, we don't have to add it again
        if (material_id := self.materials.get(name)) is not None:
            return material_id

        # If this is the first call, store the id for later reference
        n = len(self.json["appearance"]["materials"])
        self.materials[name] = n

        self.json["appearance"]["materials"].append(
            {
                "name": name,
                # "ambientIntensity": 0.4000,
                "diffuseColor": color,
                "emissiveColor": color,
                "specularColor": color,
                # "shininess": 0.0,
                # "transparency": 0,
                # "isSmooth": True,
            }
        )

        return n

    def add_landuse(self, x: int, y: int, z: int = 0, lu_type: str = "grass", object_type="LandUse") -> str:
        a = self.add_vertex(x - 50, y - 50)
        b = self.add_vertex(x + 50, y - 50)
        c = self.add_vertex(x + 50, y + 50)
        d = self.add_vertex(x - 50, y + 50)
        cityobject_id = self.new_cityobject_id()

        materials = {
            "grass": [0, 106 / 256, 78 / 256],
            "water": [0, 0, 1],
            "building": [0.5, 0.5, 0.5],
            "asphalt": [0, 0, 0],
            # ...
        }

        material_id = self.add_material(lu_type, materials[lu_type])

        object = {
            "type": object_type,
            "geometry": [
                {
                    "type": "MultiSurface",
                    "lod": "2",
                    "boundaries": [[[a, b, c, d]]],
                    "material": {f"landuse_{material_id}": {"values": [material_id]}},
                }
            ],
        }
        self.json["CityObjects"][cityobject_id] = object
        return cityobject_id

    def add_lcz1(self, x: int, y: int, z: int = 0) -> None:
        """Add compact high rise on 100m grid cells."""
        self.add_cube(x - 50, y - 50, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x - 10, y - 50, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x + 30, y - 50, scaling=(22.2, 22.2, 37.5))

        self.add_cube(x - 50, y - 10, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x - 10, y - 10, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x + 30, y - 10, scaling=(22.2, 22.2, 37.5))

        self.add_cube(x - 50, y + 30, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x - 10, y + 30, scaling=(22.2, 22.2, 37.5))
        self.add_cube(x + 30, y + 30, scaling=(22.2, 22.2, 37.5))

    def add_lcz2(self, x: int, y: int, z: int = 0) -> None:
        """Add compact mid rise on 100m grid cells."""
        self.add_cube(x - 50, y - 50, scaling=(22, 22, 14))
        self.add_cube(x - 10, y - 50, scaling=(22, 22, 14))
        self.add_cube(x + 30, y - 50, scaling=(22, 22, 14))

        self.add_cube(x - 50, y - 10, scaling=(22, 22, 14))
        self.add_cube(x - 10, y - 10, scaling=(22, 22, 14))
        self.add_cube(x + 30, y - 10, scaling=(22, 22, 14))

        self.add_cube(x - 50, y + 30, scaling=(22, 22, 14))
        self.add_cube(x - 10, y + 30, scaling=(22, 22, 14))
        self.add_cube(x + 30, y + 30, scaling=(22, 22, 14))

    def add_lcz3(self, x: int, y: int, z: int = 0) -> None:
        """Add compact low rise on 100m grid cells."""
        for dx, dy in itertools.product([-50, -35, -20, -5, 10, 25, 40], repeat=2):
            self.add_cube(x + dx, y + dy, scaling=(9.6, 9.6, 6.5))

    def add_lcz4(self, x: int, y: int, z: int = 0) -> None:
        """Add open high-rise on 100m grid cells."""
        self.add_cube(x - 50, y, scaling=(42.86, 42.86, 37.5))
        self.add_cube(x, y - 50, scaling=(42.86, 42.86, 37.5))

    def add_lcz5(self, x: int, y: int, z: int = 0) -> None:
        self.add_cube(x - 50, y - 50, scaling=(26.25, 26.25, 17.5))
        self.add_cube(x + 25, y - 50, scaling=(26.25, 26.25, 17.5))
        self.add_cube(x - 13, y - 13, scaling=(26.25, 26.25, 17.5))
        self.add_cube(x - 50, y + 25, scaling=(26.25, 26.25, 17.5))
        self.add_cube(x + 25, y + 25, scaling=(26.25, 26.25, 17.5))

    def add_lcz6(self, x: int, y: int, z: int = 0) -> None:
        self.add_cube(x - 50, y - 50, scaling=(13, 13, 6.5))
        self.add_cube(x - 25, y - 50, scaling=(13, 13, 6.5))
        self.add_cube(x, y - 50, scaling=(13, 13, 6.5))
        self.add_cube(x + 25, y - 50, scaling=(13, 13, 6.5))

        self.add_cube(x - 37, y - 37, scaling=(13, 13, 6.5))
        self.add_cube(x - 13, y - 37, scaling=(13, 13, 6.5))
        self.add_cube(x + 13, y - 37, scaling=(13, 13, 6.5))
        self.add_cube(x + 37, y - 37, scaling=(13, 13, 6.5))

        self.add_cube(x - 50, y - 25, scaling=(13, 13, 6.5))
        self.add_cube(x - 25, y - 25, scaling=(13, 13, 6.5))
        self.add_cube(x, y - 25, scaling=(13, 13, 6.5))
        self.add_cube(x + 25, y - 25, scaling=(13, 13, 6.5))

        self.add_cube(x - 37, y - 13, scaling=(13, 13, 6.5))
        self.add_cube(x - 13, y - 13, scaling=(13, 13, 6.5))
        self.add_cube(x + 13, y - 13, scaling=(13, 13, 6.5))
        self.add_cube(x + 37, y - 13, scaling=(13, 13, 6.5))

        self.add_cube(x - 50, y, scaling=(13, 13, 6.5))
        self.add_cube(x - 25, y, scaling=(13, 13, 6.5))
        self.add_cube(x, y, scaling=(13, 13, 6.5))
        self.add_cube(x + 25, y, scaling=(13, 13, 6.5))

        self.add_cube(x - 37, y + 13, scaling=(13, 13, 6.5))
        self.add_cube(x - 13, y + 13, scaling=(13, 13, 6.5))
        self.add_cube(x + 13, y + 13, scaling=(13, 13, 6.5))
        self.add_cube(x + 37, y + 13, scaling=(13, 13, 6.5))

        self.add_cube(x - 50, y + 25, scaling=(13, 13, 6.5))
        self.add_cube(x - 25, y + 25, scaling=(13, 13, 6.5))
        self.add_cube(x, y + 25, scaling=(13, 13, 6.5))
        self.add_cube(x + 25, y + 25, scaling=(13, 13, 6.5))

        self.add_cube(x - 37, y + 37, scaling=(13, 13, 6.5))
        self.add_cube(x - 13, y + 37, scaling=(13, 13, 6.5))
        self.add_cube(x + 13, y + 37, scaling=(13, 13, 6.5))
        self.add_cube(x + 37, y + 37, scaling=(13, 13, 6.5))

    def add_lcz7(self, x: int, y: int, z: int = 0) -> None:
        self.add_cube(x - 50, y - 50, scaling=(25, 25, 3))
        self.add_cube(x - 22, y - 50, scaling=(25, 25, 3))
        self.add_cube(x + 6, y - 50, scaling=(25, 25, 3))
        self.add_cube(x + 34, y - 50, scaling=(15, 25, 3))

        self.add_cube(x - 50, y - 22, scaling=(15, 25, 3))
        self.add_cube(x - 32, y - 22, scaling=(25, 25, 3))
        self.add_cube(x - 4, y - 22, scaling=(25, 25, 3))
        self.add_cube(x + 24, y - 22, scaling=(25, 25, 3))

        self.add_cube(x - 50, y + 6, scaling=(25, 25, 3))
        self.add_cube(x - 22, y + 6, scaling=(25, 25, 3))
        self.add_cube(x + 6, y + 6, scaling=(25, 25, 3))
        self.add_cube(x + 34, y + 6, scaling=(15, 25, 3))

        self.add_cube(x - 50, y + 34, scaling=(15, 15, 3))
        self.add_cube(x - 32, y + 34, scaling=(25, 15, 3))
        self.add_cube(x - 4, y + 34, scaling=(25, 15, 3))
        self.add_cube(x + 24, y + 34, scaling=(25, 15, 3))

    def add_lcz8(self, x: int, y: int, z: int = 0) -> None:
        self.add_cube(x - 45, y - 45, scaling=(28.9, 28.9, 6.5))
        self.add_cube(x + 15, y - 45, scaling=(28.9, 28.9, 6.5))
        self.add_cube(x - 15, y - 15, scaling=(28.9, 28.9, 6.5))
        self.add_cube(x - 45, y + 15, scaling=(28.9, 28.9, 6.5))
        self.add_cube(x + 15, y + 15, scaling=(28.9, 28.9, 6.5))

    def add_lcz9(self, x: int, y: int, z: int = 0) -> None:
        """Sparsely built."""
        self.add_cube(x - 45, y - 45, scaling=(43.33, 43.33, 6.5))
        self.add_cube(x + 5, y + 5, scaling=(43.33, 43.33, 6.5))

    def add_lcz10(self, x: int, y: int, z: int = 0) -> None:
        """Heavy industry."""
        self.add_cube(x - 50, y - 50, scaling=(23.8, 23.8, 10))
        self.add_cube(x, y, scaling=(23.8, 23.8, 10))

    def add_lcz(self, x: int, y: int, lcz: int):
        match lcz:
            case 51: return self.add_lcz1(x, y)
            case 52: return self.add_lcz2(x, y)
            case 53: return self.add_lcz3(x, y)
            case 54: return self.add_lcz4(x, y)
            case 55: return self.add_lcz5(x, y)
            case 56: return self.add_lcz6(x, y)
            case 57: return self.add_lcz7(x, y)
            case 58: return self.add_lcz8(x, y)
            case 59: return self.add_lcz9(x, y)
            case 61: return self.add_lcz10(x, y)
            case 17: return self.add_landuse(x, y, object_type="WaterBody")
            case 21: return self.add_landuse(x, y, object_type="WaterBody")
            case _: return self.add_landuse(x, y, object_type="LandUse")


def reproduce_prototypes():
    """Reproduce image with prototypes of LCZs."""
    filename = "prototypes.city.json"
    print("Reproducing prototypes LCZ image...")

    city = City()
    city.add_lcz1(50, 50)
    city.add_lcz2(50, 150)
    city.add_lcz3(50, 250)
    city.add_lcz4(150, 50)
    city.add_lcz5(150, 150)
    city.add_lcz6(150, 250)
    city.add_lcz7(250, 50)
    city.add_lcz8(50, 350)
    city.add_lcz9(150, 350)
    city.add_lcz10(50, 450)
    city.to_cityjson(filename)

    print(f"Result stored in {filename}")


def map_landuse():
    filename = "landusemap.city.json"
    print("Mapping landuse types")

    city = City()
    city.add_landuse(50, 50, lu_type="grass")
    city.add_landuse(150, 50, lu_type="grass")
    city.add_landuse(250, 50, lu_type="asphalt")
    city.add_landuse(50, 150, lu_type="water")
    city.add_landuse(150, 150, lu_type="water")
    city.add_landuse(250, 150, lu_type="asphalt")
    city.add_landuse(50, 250, lu_type="building")
    city.add_landuse(150, 250, lu_type="building")
    city.add_landuse(250, 250, lu_type="asphalt")
    city.to_cityjson(filename)

    print(f"Results stored in {filename}")


def generate_map():
    filename = "lcz_map.city.json"
    print("Mapping lcz raster to CityJSON")

    import numpy as np
    nx = ny = 50   # 50 switches on performance mode on ninja viewer
    xs = np.arange(nx) * 100 + 50
    ys = np.arange(ny) * 100 + 50
    lcz = np.random.randint(0, 10, size=(nx, ny))

    city = City()
    for (i, x) in enumerate(xs):
        for (j, y) in enumerate(ys):
            city.add_lcz(int(x), int(y), int(lcz[i, j]))

    city.to_cityjson(filename)
    print(f"Results stored in {filename}")

def map_amsterdam():
    filename = "lcz_amsterdam.city.json"
    print("Mapping lcz raster to CityJSON")

    import xarray as xr
    da = xr.open_dataarray('CGLC_MODIS_LCZ_cutout_NL.zarr')
    amsterdam = da.sel(X=slice(4.85, 4.92), Y=slice(52.4, 52.35))

    city = City()
    for (i, x) in enumerate(amsterdam.X):
        for (j, y) in enumerate(amsterdam.Y):
            city.add_lcz(i*100, j*-100, amsterdam[j, i].item())

    # city.json['metadata']['referenceSystem'] = "http://www.opengis.net/def/crs/EPSG/0/4326"
    city.to_cityjson(filename)
    print(f"Results stored in {filename}")

def map_manhattan():

    filename = "lcz_manhattan.city.json"
    print("Mapping lcz raster to CityJSON")

    import xarray as xr
    da = xr.open_dataarray('CGLC_MODIS_LCZ_cutout_Manhattan.zarr')
    manhattan = da.sel(X=slice(-74.05, -73.95) , Y=slice(40.80, 40.68))

    city = City()
    for (i, x) in enumerate(manhattan.X):
        for (j, y) in enumerate(manhattan.Y):
            city.add_lcz(i*100, j*-100, manhattan[j, i].item())

    # city.json['metadata']['referenceSystem'] = "http://www.opengis.net/def/crs/EPSG/0/4326"
    city.to_cityjson(filename)
    print(f"Results stored in {filename}")

if __name__ == "__main__":
    reproduce_prototypes()
    map_landuse()
    generate_map()
    map_amsterdam()
    map_manhattan()
