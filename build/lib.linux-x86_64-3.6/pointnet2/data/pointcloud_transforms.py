from __future__ import (
    division,
    absolute_import,
    with_statement,
    print_function,
    unicode_literals,
)
import random

import numpy as np
import torch


def ScaleX(pts,v): # (0 , 2)
    assert 0 <= v <= 1
    scaler = np.random.uniform(low = 1-v, high =  1 + v)
    pts[:, 0 ] *= scaler
    return pts

def ScaleY(pts,v): # (0 , 2)
    assert 0 <= v <= 1
    scaler = np.random.uniform(low = 1-v, high =  1 + v)
    pts[:, 1 ] *= scaler
    return pts

def ScaleZ(pts,v): # (0 , 2)
    assert 0 <= v <= 1
    scaler = np.random.uniform(low = 1-v, high =  1 + v)
    pts[:, 2 ] *= scaler
    return pts

def Resize(pts,v):
    assert 0 <= v <= 1
    scaler = np.random.uniform(low = 1-v, high =  1 + v)
    pts[:, 0:3 ] *= scaler
    return pts

def NonUniformScale(pts,v): # Resize in [0.5 , 1.5]
    assert 0 <= v <= 1
    scaler = np.random.uniform( low = 1 - v, high =  1 + v, size = 3 )
    pts[:, 0:3] *= torch.from_numpy(scaler).float()
    return pts



def angle_axis(angle, axis):
    # type: (float, np.ndarray) -> float
    """Returns a 4x4 rotation matrix that performs a rotation around axis by angle

    Parameters
    ----------
    angle : float
        Angle to rotate by
    axis: np.ndarray
        Axis to rotate about

    Returns
    -------
    torch.Tensor
        3x3 rotation matrix
    """
    u = axis / np.linalg.norm(axis)
    cosval, sinval = np.cos(angle), np.sin(angle)

    # yapf: disable
    cross_prod_mat = np.array([[0.0, -u[2], u[1]],
                                [u[2], 0.0, -u[0]],
                                [-u[1], u[0], 0.0]])

    R = torch.from_numpy(
        cosval * np.eye(3)
        + sinval * cross_prod_mat
        + (1.0 - cosval) * np.outer(u, u)
    )
    # yapf: enable
    return R.float()

def RotateX(points,v): # ( 0 , 2 * pi)
    assert 0 <= v <= 2 * np.pi
    if np.random.random() > 0.5:
        v *= -1
    axis = np.array([1. , 0. , 0.])

    rotation_angle = np.random.uniform() * v
    rotation_matrix = angle_axis(rotation_angle, axis)

    normals = points.size(1) > 3
    if not normals:
        return torch.matmul(points, rotation_matrix.t())
    else:
        pc_xyz = points[:, 0:3]
        pc_normals = points[:, 3:]
        points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
        points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

        return points

def RotateY(points,v): # ( 0 , 2 * pi)
    assert 0 <= v <= 2 * np.pi
    if np.random.random() > 0.5:
        v *= -1
    axis = np.array([0. , 1. , 0.])

    rotation_angle = np.random.uniform() * v
    rotation_matrix = angle_axis(rotation_angle, axis)

    normals = points.size(1) > 3
    if not normals:
        return torch.matmul(points, rotation_matrix.t())
    else:
        pc_xyz = points[:, 0:3]
        pc_normals = points[:, 3:]
        points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
        points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

        return points


def RotateZ(points,v): # ( 0 , 2 * pi)
    assert 0 <= v <= 2 * np.pi
    if np.random.random() > 0.5:
        v *= -1
    axis = np.array([0. , 0. , 1.])

    rotation_angle = np.random.uniform() * v
    rotation_matrix = angle_axis(rotation_angle, axis)

    normals = points.size(1) > 3
    if not normals:
        return torch.matmul(points, rotation_matrix.t())
    else:
        pc_xyz = points[:, 0:3]
        pc_normals = points[:, 3:]
        points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
        points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

        return points

def RandomAxisRotation(points,v):
    assert 0 <= v <= 2 * np.pi
    axis = np.random.randn(3)
    axis /= np.sqrt((axis**2).sum())

    rotation_angle = np.random.uniform() * v
    rotation_matrix = angle_axis(rotation_angle, axis)

    normals = points.size(1) > 3
    if not normals:
        return torch.matmul(points, rotation_matrix.t())
    else:
        pc_xyz = points[:, 0:3]
        pc_normals = points[:, 3:]
        points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
        points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

        return points

def RotatePerturbation(points,v):
    assert 0 <= v <= 10
    angle_sigma = 0.008 * v
    angle_clip = 0.01 * v

    angles = np.clip(angle_sigma * np.random.randn(3), -angle_clip, angle_clip)
    Rx = angle_axis(angles[0], np.array([1.0, 0.0, 0.0]))
    Ry = angle_axis(angles[1], np.array([0.0, 1.0, 0.0]))
    Rz = angle_axis(angles[2], np.array([0.0, 0.0, 1.0]))

    rotation_matrix = torch.matmul(torch.matmul(Rz, Ry), Rx)

    normals = points.size(1) > 3
    if not normals:
        return torch.matmul(points, rotation_matrix.t())
    else:
        pc_xyz = points[:, 0:3]
        pc_normals = points[:, 3:]
        points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
        points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

        return points


def Jitter(points,v):
    assert 0.0 <= v <= 10
    mu = 0
    sigma = 0.01 * v
    clip = 0.005 * v

    jitter = np.clip(
        sigma * np.random.randn(points.size(0),3) + mu,
        -clip, clip )

    points[:, 0:3] += torch.from_numpy(jitter).float()
    return points

def PointToNoise(points,v):
    assert 0 <= v <= 0.5

    mask = torch.randn(points.size(0)) < v
    for i in range(mask.size(0)):
        if mask[i]:
            points[i,0:3] = torch.randn(3)
    return points


def TranslateX(points ,v):
    assert 0 <= v <= 1
    translation = (2 * np.random.random() - 1 ) * v
    points[:, 0] += translation
    return points

def TranslateY(points ,v):
    assert 0 <= v <= 1
    translation = (2 * np.random.random() - 1 ) * v
    points[:, 1 ] += translation
    return points

def TranslateZ(points ,v):
    assert 0 <= v <= 1
    translation = (2 * np.random.random() - 1 ) * v
    points[:, 2 ] += translation
    return points

def NonUniformTranslate(points ,v):
    assert 0 <= v <= 1
    translation = (2 * np.random.random(3) - 1 ) * v
    points[:, 0:3] += torch.from_numpy(translation).float()
    return points

def RandomDropout(points,v):
    assert 0.5 <= v <= 0.875
    dropout_rate = v
    drop = np.random.random(points.size(0)) < dropout_rate
    save = [idx for idx, boolean in enumerate(drop) if not boolean]
    points[drop] = points[save[0]]
    return points

def RandomErase(points,v):
    assert 0 <= v <= 0.5
    "v : the radius of erase ball"
    random_idx = np.random.randint(points.size(0))
    mask = ((points[:,0:3] - points[random_idx,0:3])**2).sum(axis = 1) < v ** 2
    points[mask] = points[random_idx]
    return points

def DBSCAN(points,v):
    "https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html"
    assert 0 <= v <= 10
    from sklearn.cluster import DBSCAN
    eps = 0.05 * v
    min_samples = 2 * v
    clustering = DBSCAN(eps = eps , min_samples = min_samples).fit(points[:,0:3])
    for label in set(clustering.labels_):
        if label == -1:
            continue
        mask = (clustering.labels_ == label)
        points[mask,0:3] = torch.mean(points[mask,0:3])

    return points

def ShearXY(points,v):
    assert 0 <= v <= 0.5
    a , b  = v * (2 * np.random.random(2) - 1)
    shear_matrix = np.array([[1, 0, 0],
                             [0, 1, 0],
                             [a, b, 1]])
    shear_matrix = torch.from_numpy(shear_matrix).float()
    points[:,0:3] = points[:, 0:3] @ shear_matrix.t()
    return points

def ShearYZ(points,v):
    assert 0 <= v <= 0.5
    b , c  = v * (2 * np.random.random(2) - 1)
    shear_matrix = np.array([[1, b, c],
                             [0, 1, 0],
                             [0, 0, 1]])
    shear_matrix = torch.from_numpy(shear_matrix).float()
    points[:,0:3] = points[:, 0:3] @ shear_matrix.t()

    return points

def ShearXZ(points,v):
    assert 0 <= v <= 0.5
    a , c  = v * (2 * np.random.random(2) - 1)
    shear_matrix = np.array([[1, 0, 0],
                             [a, 1, c],
                             [0, 0, 1]])
    shear_matrix = torch.from_numpy(shear_matrix).float()
    points[:,0:3] = points[:, 0:3] @ shear_matrix.t()
    return points


def GlobalAffine(points,v):
    assert 0 <= v <= 0.01

    affine_matrix = torch.from_numpy(np.eye(3) + np.random.randn(3,3) * v ).float()
    points[:,0:3] = points[:, 0:3] @ affine_matrix.t()

    return points

def GridDistortion(points,v):
    pass

def ElasticDeformation(points,v):
    pass


# def PiecewiseShear(points,v):
#     assert 0 <= v <= 10
#
#     radius = 0.01 * int(v)
#     n_piece = 5 * int(v)
#     magnitude = 0.05 * v
#
#     for _ in range(n_piece):
#         pts = points[:,0:3]
#         centroid_pt = pts[np.random.randint(points.size(0))]
#         box_idx = ((torch.abs(pts - centroid_pt) < radius ).sum(axis=1) == 3 )
#
#         shear_lst = [ShearXY , ShearXZ , ShearYZ]
#         shear_choice = random.choices(shear_lst, k = 1)
#         for op in shear_choice:
#             points[box_idx,0:3] = op(pts[box_idx], magnitude)
#
#     return points
