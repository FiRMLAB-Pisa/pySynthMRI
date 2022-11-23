import os.path

import numpy as np


def reorder_img(img, resample=None):
    """Returns an image with the affine diagonal (by permuting axes).
    The orientation of the new image will be RAS (Right, Anterior, Superior).
    If it is impossible to get xyz ordering by permuting the axes, a
    'ValueError' is raised.
    Parameters
    -----------
    img : Niimg-like object
        See http://nilearn.github.io/manipulating_images/input_output.html
        Image to reorder.
    resample : None or string in {'continuous', 'linear', 'nearest'}, optional
        If resample is None (default), no resampling is performed, the
        axes are only permuted.
        Otherwise resampling is performed and 'resample' will
        be passed as the 'interpolation' argument into
        resample_img.
    """

    # The copy is needed in order not to modify the input img affine
    # see https://github.com/nilearn/nilearn/issues/325 for a concrete bug
    affine = img.affine.copy()
    data = img.copy()

    axis_numbers = np.argmax(np.abs(data), axis=0)
    while not np.all(np.sort(axis_numbers) == axis_numbers):
        first_inversion = np.argmax(np.diff(axis_numbers) < 0)
        axis1 = first_inversion + 1
        axis2 = first_inversion
        data = np.swapaxes(data, axis1, axis2)
        order = np.array((0, 1, 2, 3))
        order[axis1] = axis2
        order[axis2] = axis1
        affine = affine.T[order].T
        axis_numbers = np.argmax(np.abs(data), axis=0)
    #
    # # Now make sure the affine is positive
    # pixdim = np.diag(data).copy()
    # if pixdim[0] < 0:
    #     b[0] = b[0] + pixdim[0]*(data.shape[0] - 1)
    #     pixdim[0] = -pixdim[0]
    #     slice1 = slice(None, None, -1)
    # else:
    #     slice1 = slice(None, None, None)
    # if pixdim[1] < 0:
    #     b[1] = b[1] + pixdim[1]*(data.shape[1] - 1)
    #     pixdim[1] = -pixdim[1]
    #     slice2 = slice(None, None, -1)
    # else:
    #     slice2 = slice(None, None, None)
    # if pixdim[2] < 0:
    #     b[2] = b[2] + pixdim[2]*(data.shape[2] - 1)
    #     pixdim[2] = -pixdim[2]
    #     slice3 = slice(None, None, -1)
    # else:
    #     slice3 = slice(None, None, None)
    # data = data[slice1, slice2, slice3]

    return data


def to_matrix_vector(transform):
    """Split an homogeneous transform into its matrix and vector components.
    The transformation must be represented in homogeneous coordinates.
    It is split into its linear transformation matrix and translation vector
    components.
    This function does not normalize the matrix. This means that for it to be
    the inverse of from_matrix_vector, transform[-1, -1] must equal 1, and
    transform[-1, :-1] must equal 0.
    Parameters
    ----------
    transform : numpy.ndarray
        Homogeneous transform matrix. Example: a (4, 4) transform representing
        linear transformation and translation in 3 dimensions.
    Returns
    -------
    matrix, vector : numpy.ndarray
        The matrix and vector components of the transform matrix.  For
        an (N, N) transform, matrix will be (N-1, N-1) and vector will be
        a 1D array of shape (N-1,).
    See Also
    --------
    from_matrix_vector
    """
    ndimin = transform.shape[0] - 1
    ndimout = transform.shape[1] - 1
    matrix = transform[0:ndimin, 0:ndimout]
    vector = transform[0:ndimin, ndimout]
    return matrix, vector


def from_matrix_vector(matrix, vector):
    """Combine a matrix and vector into a homogeneous transform.
    Combine a rotation matrix and translation vector into a transform
    in homogeneous coordinates.
    Parameters
    ----------
    matrix : numpy.ndarray
        An (N, N) array representing the rotation matrix.
    vector : numpy.ndarray
        A (1, N) array representing the translation.
    Returns
    -------
    xform: numpy.ndarray
        An (N+1, N+1) transform matrix.
    See Also
    --------
    nilearn.resampling.to_matrix_vector
    """
    nin, nout = matrix.shape
    t = np.zeros((nin + 1, nout + 1), matrix.dtype)
    t[0:nin, 0:nout] = matrix
    t[nin, nout] = 1.
    t[0:nin, nout] = vector
    return t


def get_unique_filename(filename_path):
    postfix = 1
    new_filename_path = filename_path
    while os.path.exists(new_filename_path):
        new_filename_path = filename_path[:-4] + "_" + str(postfix) + ".png"
        postfix += 1
    return new_filename_path
