import glm
import random

def get_broad_collision(collider1, collider2):
    #if glm.length(collider1.geometric_center - collider2.geometric_center) <= glm.length(collider1.dimensions) + glm.length(collider2.dimensions): print(f'true{random.randint(1, 100)}')
    return glm.length(collider1.geometric_center - collider2.geometric_center) < glm.length(collider1.dimensions) ** 2 + glm.length(collider2.dimensions) ** 2