import sys
from typing import Tuple, List


import numpy as np
from pytest import fixture, mark

from madcad.prelude import *
import madcad as cad

from madcad.draft import draft_by_slice, draft_extrusion, draft_by_axis, _extrude


PLOT_DEFUALT = "--trace" in sys.argv or __name__ == "__main__" or "-v" in sys.argv


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
		Mesh(points[:3], [[1, 0, 2]]).own(points=True),
		Web(points, [(0, 1), (1, 2), (2, 0)]).own(points=True),
	]
	return bases


@fixture
def bases() -> List:
	"for extrusions"
	return make_bases()


@fixture(params=[0, 1, 2])
def base(bases, request) -> Mesh:
	"for extrusions"
	yield bases[request.param]


@fixture()
def ex(base) -> Mesh:
	trans = Z * 2
	yield cad.extrusion(trans, base).finish()


@fixture
def meshes(bases) -> List[Mesh]:
	trans = Z * 2
	extrudes = [cad.extrusion(trans, base).finish() for base in bases]
	cube = cad.brick(width=3)
	cylinder = cad.cylinder(vec3(0, 0, 0), vec3(0, 0, 3), 1).finish()
	yield extrudes + [cube, cylinder]


@fixture(params=range(5))
def mesh(meshes, request) -> Mesh:
	yield meshes[request.param]


@mark.skip
def test_mesh(mesh):
	"For checking that input to test functions is sound"
	plot_normals(mesh)


def check_draft(drafted, angle, normal, plot):
	result_angles = draft_angles(drafted, normal, degrees=True)

	for a in result_angles:
		print(a)

	if plot:
		show([drafted], projection=cad.rendering.Orthographic())
		# plot_normals(drafted)

	angle_set = set(result_angles)
	expected_angles = {0.0, 90.0 - angle, 90.0 + angle, 180.0}
	assert angle_set <= expected_angles


def test_draft_extrusion(base: Mesh | Web | Wire, plot=PLOT_DEFUALT):
	angle = 5
	drafted = draft_extrusion(base, Z * 2 , angle)
	check_draft(drafted, angle, Z, plot)


def test_draft_slice(ex: Mesh, plot=PLOT_DEFUALT):
	angle = 5
	drafted = draft_by_slice(ex, angle)
	check_draft(drafted, angle, Z, plot)


def test_draft_axis(mesh: Mesh, plot=PLOT_DEFUALT):
	axis = Axis(vec3(0, 0, 1), Z)
	angle = 5
	drafted = draft_by_axis(mesh, axis, angle)
	check_draft(drafted, angle, Z, plot)


def draft_angles(mesh: Mesh, n: vec3, **kwargs):
	return [angle_vectors(n, face_n, **kwargs) for face_n in mesh.facenormals()]


def plot_normals(mesh: Mesh):
	arrows = []
	for face in mesh.faces:
		center = sum(mesh.facepoints(face)) / 3
		n = mesh.facenormal(face)
		cyl = cad.cylinder(center, center + n * 0.2, 0.05)
		arrows.append(cyl)

	show([mesh] + arrows)


def angle_vectors(v1: vec3, v2: vec3, degrees=False) -> float:
	n1 = normalize(v1)
	n2 = normalize(v2)
	angle = np.arccos(dot(n1, n2))
	if not degrees:
		return angle
	return np.rad2deg(angle)


def test_extrude(base, plot=PLOT_DEFUALT):
	ex, edges = _extrude(base, Z)
	if plot:
		show([ex])
		plot_normals(ex)

if __name__ == "__main__":
	base = make_bases()[1]
	test_draft_extrusion(base)
	test_extrude(base)
