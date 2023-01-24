import sys
from typing import Tuple, List


import numpy as np
from pytest import fixture

from madcad.prelude import *
import madcad as cad

from madcad.draft import draft_by_slice

PLOT_DEFUALT = "--trace" in sys.argv


def make_extrusions() -> List[Tuple[Mesh, type]]:
	points = tlist(
		[
			[0, 0, 0],
			[1, 0, 0],
			[1, 1, 0],
			[0, 1, 0],
		],
		dtype=vec3,
	)
	bases = [
		Wire(points).own(points=True),
		Mesh(points[:3], [[0, 1, 2]]).own(points=True),
		Web(points, [(0, 1), (1, 2), (2, 0)]).own(points=True),
	]
	trans = Z * 5
	return [cad.extrusion(trans, b).finish() for b in bases]


@fixture(scope="module", params=make_extrusions())
def ex(request) -> Mesh:
	yield request.param


def test_draft_slice(ex: Tuple[Mesh, type], plot=PLOT_DEFUALT):
	draft_angle = 5
	drafted = draft_by_slice(ex, draft_angle)
	angles = draft_angles(drafted, Z, degrees=True)

	for a in angles:
		print(a)

	if plot:
		show([drafted])

	angle_set = set(angles)
	expected_angles = {0.0, 90.0 - draft_angle, 90.0 + draft_angle, 180.0}
	assert angle_set <= expected_angles


def draft_angles(mesh: Mesh, n: vec3, **kwargs):
	return [angle_vectors(n, face_n, **kwargs) for face_n in mesh.facenormals()]


def angle_vectors(v1: vec3, v2: vec3, degrees=False) -> float:
	n1 = normalize(v1)
	n2 = normalize(v2)
	angle = np.arccos(dot(n1, n2))
	if not degrees:
		return angle
	return np.rad2deg(angle)


if __name__ == "__main__":

	drafts = make_drafts()

	for drafted in drafts:
		test_draft(drafted, True)
