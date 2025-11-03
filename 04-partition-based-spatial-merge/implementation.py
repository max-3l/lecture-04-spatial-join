from rtree.rtree import Point, MinimalBoundingRectangle
from typing import List, Tuple

def prepare(points_a: List[Point], points_b: List[Point], grid_axis_divisions: int=100) -> dict:
    return {"points_a": points_a, "points_b": points_b, "grid_axis_divisions": grid_axis_divisions}

def partition(points: List[Point], num_divs: int, full_mbr: MinimalBoundingRectangle) -> List[List[Point]]:
    partitions = [[[] for _ in range(num_divs)] for _ in range(num_divs)]
    def get_coords(point_x, point_y) -> Tuple[int,int]:
        x_coord = min(int((point_x - full_mbr.x1)/(full_mbr.x2 - full_mbr.x1) * num_divs), num_divs - 1)
        y_coord = min(int((point_y - full_mbr.y1)/(full_mbr.y2 - full_mbr.y1) * num_divs), num_divs - 1)
        assert(x_coord >= 0 and y_coord >= 0)
        assert(x_coord < num_divs and y_coord < num_divs)
        return x_coord, y_coord
    for point in points:
        first_x_coord, first_y_coord = get_coords(point.mbr.x1, point.mbr.y1)
        last_x_coord, last_y_coord = get_coords(point.mbr.x2, point.mbr.y2)
        for x_coord in range(first_x_coord, last_x_coord + 1):
            for y_coord in range(first_y_coord, last_y_coord + 1):
                partitions[x_coord][y_coord].append(point)
    return partitions

def join(prepared: dict) -> List[Tuple[Point, Point]]:
    # Create grid cells
    result = []
    points_a = prepared["points_a"]
    points_b = prepared["points_b"]
    full_mbr = MinimalBoundingRectangle(
        x1=min(min(point.mbr.x1 for point in points_a), min(point.mbr.x1 for point in points_b)),
        x2=max(max(point.mbr.x2 for point in points_a), max(point.mbr.x2 for point in points_b)),
        y1=min(min(point.mbr.y1 for point in points_a), min(point.mbr.y1 for point in points_b)),
        y2=max(max(point.mbr.y2 for point in points_a), max(point.mbr.y2 for point in points_b))
    )
    num_divs = prepared["grid_axis_divisions"]
    partitions_a = partition(points_a, num_divs, full_mbr)
    partitions_b = partition(points_b, num_divs, full_mbr)
    print("Partitioned!")
    for column_a, column_b in zip(partitions_a, partitions_b):
        for tile_a, tile_b in zip(column_a, column_b):
            for point_a in tile_a:
                result.extend((point_a, point_b) for point_b in tile_b if point_a.mbr.intersects(point_b.mbr))
    # Remove duplicates via id since dataset contains duplicates that set() would filter
    seen = set()
    unique_result = []
    for pair in result:
        pair_id = (id(pair[0]), id(pair[1]))
        if pair_id not in seen:
            seen.add(pair_id)
            unique_result.append(pair)
    
    return unique_result
