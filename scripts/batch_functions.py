import numpy as np
from numba import njit

@njit
def get_empty_batch():
    return np.zeros(shape=(100_000, 19), dtype='f4')


def combine_batch_data(vbo_list, model_list):
    batch_data = get_empty_batch()
    
    vertex_index = 0

    for i in range(len(vbo_list)):
        vertex_data = vbo_list[i]
        model_data = model_list[i]

        num_vertices = vertex_data.shape[0]

        batch_data[vertex_index:vertex_index+num_vertices,:8] = vertex_data
        batch_data[vertex_index:vertex_index+num_vertices,8:] = model_data

        vertex_index += num_vertices

    return batch_data


@njit
def get_vertex_array(vertex_data, object_data):
    vertex_data = np.copy(vertex_data)
    object_data = np.array(object_data, dtype='f4')

    combined_data = np.zeros(shape=(vertex_data.shape[0], 19), dtype='f4')
    combined_data[:,:8] = vertex_data
    combined_data[:,8:] = object_data

    return combined_data