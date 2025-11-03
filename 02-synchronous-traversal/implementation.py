import itertools
from rtree.rtree import Node, Point, RTree
from typing import List, Tuple

def prepare(points_a: List[Point], points_b: List[Point]) -> dict:
    rtree_a = RTree(node_capacity=32)
    rtree_a.bulk_load(points_a)

    rtree_b = RTree(node_capacity=32)
    rtree_b.bulk_load(points_b)

    return {"rtree_a": rtree_a, "rtree_b": rtree_b}

def join(prepared: dict) -> List[Tuple[Point, Point]]:
    result = []
    rtree_a: RTree = prepared["rtree_a"]
    rtree_b: RTree = prepared["rtree_b"]

    root_a = rtree_a.root
    root_b = rtree_b.root

    def recurse_over_childs(children_a: List[Node | Point], children_b: List[Node | Point]):
        for child_a in children_a:
            for child_b in children_b:
                if child_a.mbr.intersects(child_b.mbr):
                    if child_a.is_leaf():
                        for a_i in child_a.children:
                            for b_i in child_b.children:
                                if a_i.mbr.intersects(b_i.mbr):
                                    result.append([a_i, b_i])
                    else:
                        recurse_over_childs(children_a=child_a.children, children_b=child_b.children)

    recurse_over_childs(root_a.children, root_b.children)

    return result
