import glm
import random

# main collision function
def get_narrow_collision(points1:list, points2:list, position1:glm.vec3, position2:glm.vec3) -> tuple:
    """returns the normalized normal vector of the collision and the distance"""
    have_collided, simplex = get_gjk_collision(points1, points2, position1, position2)
    if not have_collided: return glm.vec3(0, 0, 0), 0, glm.vec3(0, 0, 0)
    return get_epa_from_gjk(points1, points2, simplex)

# main gjk handler
def get_gjk_collision(points1:list, points2:list, position1:glm.vec3, position2:glm.vec3, iterations:int = 50) -> tuple:
    """gets boolean and simplex from gjk"""
    # gets starting values
    direction_vector = position1 - position2
    simplex = [get_support_point(points1, points2, direction_vector)]
    # points direction vector to the origin
    direction_vector = -simplex[0]
    # main gjk loop
    for _ in range(iterations):
        # gets support point and checks if its across the origin
        test_point = get_support_point(points1, points2, direction_vector)
        if glm.dot(test_point, direction_vector) < 0: return False, simplex
        # if successful add point and handle simplex
        simplex.append(test_point)
        check, direction_vector, simplex = handle_simplex(simplex)
        if check: return True, simplex
    return False, simplex

# simplex handling
def handle_simplex(simplex:list) -> tuple:
    """calls proper functions for gjk simplex based on size"""
    match len(simplex):
        case 2: return handle_simplex_line(simplex)
        case 3: return handle_simplex_triangle(simplex)
        case 4: return handle_simplex_tetra(simplex)
        case _: assert False, 'simplex has unsupported size :('
        
def handle_simplex_line(simplex:list) -> tuple:
    """returns perpendicular vector to simplex line"""
    vector_ab = simplex[1] - simplex[0]
    return False, triple_product(vector_ab, -simplex[0], vector_ab), simplex

def handle_simplex_triangle(simplex:list) -> tuple:
    """returns triangle normal vector pointed towards the origin"""
    directional_vector = glm.cross(simplex[1] - simplex[0], simplex[2] - simplex[0])
    return False, -directional_vector if glm.dot(directional_vector, -simplex[0]) < 0 else directional_vector, simplex

def handle_simplex_tetra(simplex:list) -> tuple:
    """runs collision test and removes point if false"""
    vec_da = simplex[3] - simplex[0]
    vec_db = simplex[3] - simplex[1]
    vec_dc = simplex[3] - simplex[2]
    vec_do = -simplex[3]
    
    epsilon = -1e-4
    
    # Randomize the order of checking the vectors
    vectors = [(glm.cross(vec_db, vec_dc), 0), (glm.cross(vec_dc, vec_da), 1), (glm.cross(vec_da, vec_db), 2)]
    random.shuffle(vectors)
    
    for normal_vec, index in vectors:
        dot_product = glm.dot(normal_vec, vec_do)
        if dot_product > epsilon:
            simplex.pop(index)
            return False, normal_vec, simplex
    return True, None, simplex

# main epa handler
def get_epa_from_gjk(points1:list, points2:list, polytope:list) -> tuple:
    """gets normal and distance from expanding polytope expansion"""
    # each list indexes the points of a face, always the same for converted simplexes
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # calculate face normals
    avg_pt = get_average_point(polytope)
    normals = [calculate_polytope_normal(face, polytope, avg_pt) for face in faces]
    # minimum collision response variables
    while True: 
        nearest_normal, nearest_distance, nearest_face = get_nearest(polytope, faces, normals)
        new_point = get_support_point(points1, points2, nearest_normal)
        # tests new point distance
        if glm.length(new_point) - nearest_distance < 0 or new_point in polytope:
            # find contact points
            contact_point1 = calculate_contact_points(points1, points2, polytope, nearest_face, nearest_normal) 
            return nearest_normal, nearest_distance, contact_point1
        polytope.append(new_point) # add support point to polytope
        faces, normals = get_new_faces_and_normals(faces, normals, polytope) # find new faces on polytope
    
# polytope handling
def get_nearest(polytope:list, faces:list, normals:list) -> int:
    """returns the normal and distance of nearest face"""
    nearest, nearest_distance, nearest_face = None, 1e10, None
    for i, face in enumerate(faces):
        if (distance := abs(glm.dot(polytope[face[0]], normals[i]))) < nearest_distance: nearest, nearest_distance, nearest_face = normals[i], distance, face
    return nearest, nearest_distance, nearest_face

def calculate_contact_points(points1, points2, polytope, face, normal):
    """Calculates the contact points on the original objects."""
    # Get the vertices of the nearest face
    a, b, c = polytope[face[0]], polytope[face[1]], polytope[face[2]]
    
    # Calculate the barycentric coordinates
    area_abc = glm.length(glm.cross(b - a, c - a))
    area_pbc = glm.length(glm.cross(b - normal, c - normal))
    area_pca = glm.length(glm.cross(c - normal, a - normal))
    
    u = area_pbc / area_abc
    v = area_pca / area_abc
    w = 1.0 - u - v
    
    # Calculate support points for each shape at the vertices of the nearest face
    support1 = get_support_point(points1, points2, a)
    support2 = get_support_point(points1, points2, b)
    support3 = get_support_point(points1, points2, c)
    
    # interpolate the contact points on the original shapes
    return u * support1 + v * support2 + w * support3

def get_new_faces_and_normals(faces:list, normals:list, polytope:list) -> tuple:
    """
    returns new faces and normals of polytope with added point
    polytope must contain recent support point as last index
    """
    sp_index, visible_indexes = len(polytope) - 1, []
    for i, normal in enumerate(normals):
        avg_point = (polytope[faces[i][0]] + polytope[faces[i][1]] + polytope[faces[i][2]]) / 3
        if glm.dot(normal, polytope[sp_index]) < 1e-5 or glm.dot(polytope[sp_index] - avg_point, normal) < 1e-5: continue
        visible_indexes.append(i)
    visible_indexes.sort() # sort for removing
    # finds new edges
    edges = []
    for i in visible_indexes:
        for edge in get_face_edges(faces[i]):
            if edge in edges: edges.remove(edge)
            else: edges.append(edge)
    # remove visible faces
    while len(visible_indexes) > 0:
        faces.pop(visible_indexes[-1])
        normals.pop(visible_indexes[-1])
        visible_indexes.pop()
    # adds new faces
    for edge in edges: faces.append((edge[0], edge[1], sp_index))
    # calculate new normals
    avg_pt = get_average_point(polytope)
    for face in faces[len(normals):]: normals.append(calculate_polytope_normal(face, polytope, avg_pt))
    return faces, normals

def get_face_edges(face:list) -> list:
    """returns the edge indexes to the polytope points"""
    return [(one, two) if (one := face[i - 1]) < (two := face[i]) else (two, one) for i in range(3)]

# mathmatical functions
def triple_product(vector1, vector2, vector3) -> glm.vec3:
    """computes (1 x 2) x 3"""
    return glm.cross(glm.cross(vector1, vector2), vector3)

def get_center_point(polytope:list) -> glm.vec3: # not being used at the moment
    """returns the center of a convex polytope"""
    minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
    for point in polytope:
        for i in range(3):
            if point[i] > maximums[i]: maximums[i] = point[i]
            if point[i] < minimums[i]: minimums[i] = point[i]
    vec = glm.vec3(*[(maximums[i] + minimums[i]) / 2 for i in range(3)])
    return vec

def get_average_point(polytope:list) -> glm.vec3:
    """returns the average of a convex polytope"""
    total_point = glm.vec3(0, 0, 0)
    for vector in polytope: total_point += vector
    return total_point / len(polytope)

def calculate_polytope_normal(face:list, polytope:list, reference_center:glm.vec3) -> glm.vec3:
    """calculates the given normal from 3 points on the polytope"""
    one, two, three = polytope[face[0]], polytope[face[1]], polytope[face[2]]
    normal = glm.cross(one-two, one-three)
    # calculate average point
    if glm.dot((one + two + three)/3 - reference_center, normal) < 0: normal *= -1
    return glm.normalize(normal)
    
# getting support points
def get_support_point(points1:list, points2:list, direction_vector:glm.vec3) -> glm.vec3:
    """gets next point on a simplex"""
    return get_furthest_point(points1, direction_vector) - get_furthest_point(points2, -direction_vector) # second vector is negative

def get_furthest_point(points:list, direction_vector:glm.vec3) -> glm.vec3: # may need to be normalized
    """finds furthest point in given direction"""
    best_point, best_dot = glm.vec3(0, 0, 0), -1e6
    for point in points: 
        if (dot := glm.dot(point, direction_vector)) > best_dot: best_point, best_dot = point, dot
    return best_point