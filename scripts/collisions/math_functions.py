import glm

# getting support points
def get_support_point(points1:list, points2:list, direction_vector:glm.vec3) -> glm.vec3:
    """gets next point on a simplex"""
    point1, point2 = get_furthest_point(points1, direction_vector), get_furthest_point(points2, -direction_vector) # second vector is negative
    return (point1 - point2, point1, point2)

def get_furthest_point(points:list, direction_vector:glm.vec3) -> glm.vec3: # may need to be normalized
    """finds furthest point in given direction"""
    best_point, best_dot = glm.vec3(0, 0, 0), -1e6
    for point in points: 
        if (dot := glm.dot(point, direction_vector)) > best_dot: best_point, best_dot = point, dot
    return best_point

# simple vector math
def get_average_point(polytope:list) -> glm.vec3:
    """returns the average of a convex polytope"""
    total_point = glm.vec3(0, 0, 0)
    for vector in polytope: total_point += vector[0]
    return total_point / len(polytope)

def triple_product(vector1, vector2, vector3) -> glm.vec3:
    """computes (1 x 2) x 3"""
    return glm.cross(glm.cross(vector1, vector2), vector3)

# line functions
def is_ccw_turn(a:glm.vec2, b:glm.vec2, c:glm.vec2) -> bool:
    """determines if the series of points results in a left hand turn"""
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) > 0 # TODO check formula