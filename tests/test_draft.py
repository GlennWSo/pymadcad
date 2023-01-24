import sys
from typing import Tuple, List


import numpy as np
from pytest import fixture

from madcad.prelude import *
import madcad as cad

from madcad.draft import draft_by_slice, draft_extrusion

PLOT_DEFUALT = "--trace" in sys.argv


def make_bases() -> List:
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
	return bases


def make_extrusions() -> List[Tuple[Mesh, type]]:
	bases = make_bases()
	trans = Z * 5
	return [cad.extrusion(trans, b).finish() for b in bases]


@fixture(scope="module", params=make_extrusions())
def ex(request) -> Mesh:
	yield request.param


@fixture(scope="module", params=make_bases())
def base(request) -> Mesh:
	yield request.param


def check_draft(drafted, angle):
	result_angles = draft_angles(drafted, Z, degrees=True)

	for a in result_angles:
		print(a)


	angle_set = set(result_angles)
	expected_angles = {0.0, 90.0 - angle, 90.0 + angle, 180.0}
	assert angle_set <= expected_angles

def test_draft_extrusion(base: Mesh, plot=PLOT_DEFUALT):
	angle = 5
	drafted = draft_extrusion(Z*5, base, angle)
	if plot:
		show([drafted])
	check_draft(drafted, angle)

def test_draft_slice(ex: Tuple[Mesh, type], plot=PLOT_DEFUALT):
	angle = 5
	drafted = draft_by_slice(ex, angle)
	if plot:
		show([drafted])
	check_draft(drafted, angle)


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
