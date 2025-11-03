import math
from rtree.rtree import Node, Point, RTree, MinimalBoundingRectangle
from typing import List, Tuple

def prepare(points_a: List[Point], points_b: List[Point]) -> dict:
    rtree_a = RTree(node_capacity=32)
    rtree_a.bulk_load(points_a)

    return {"rtree_a": rtree_a, "points_b": points_b, "leaf_size": 32}

def join(prepared: dict) -> List[Tuple[Point, Point]]:
    result = []
    rtree_a: RTree = prepared["rtree_a"]
    points_b = prepared["points_b"]
    leaf_size = prepared["leaf_size"]
    
    points = sorted(points_b, key=lambda p: p.x)
    number_of_leafs = math.ceil(len(points) / leaf_size)
    num_slices = math.ceil(number_of_leafs ** 0.5)
    slice_size = (len(points) + num_slices - 1) // num_slices
    slices = [points[i * slice_size:(i + 1) * slice_size] for i in range(num_slices)]

    def find_intersecting_nodes(slice: MinimalBoundingRectangle, node: Node):
        intersecting_nodes = []
        if not node.is_leaf():
            for child in node.children:
                intersecting_nodes.extend(find_intersecting_nodes(slice, child))
        else:
            if node.mbr.intersects(slice):
                intersecting_nodes.append(node)
        
        return intersecting_nodes

    root = rtree_a.root
    if not root:
        return []

    for slice in slices:
        slice_node = Node(mbr=None, children=slice)
        slice_node.update_mbr()

        intersecting_nodes = find_intersecting_nodes(buffer_mbr(slice_node.mbr, max(slice, key=lambda p: p.radius).radius), root)

        for node in intersecting_nodes:
            for s_point in slice:
                for n_point in node.children:
                    if s_point.mbr.intersects(n_point.mbr):
                        result.append((n_point, s_point))

    return result

def buffer_mbr(mbr: MinimalBoundingRectangle, buffer: float) -> MinimalBoundingRectangle:
    return MinimalBoundingRectangle(
        mbr.x1 - buffer,
        mbr.y1 - buffer,
        mbr.x2 + buffer,
        mbr.y2 + buffer
    )