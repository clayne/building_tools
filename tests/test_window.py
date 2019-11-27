import bpy
import math
import bmesh
import random
import operator as op

from mathutils import Vector, Matrix
from ..core.window import WindowProperty
from ..core.window.window_types import create_window
from ..utils import (
    plane,
    bm_to_obj,
    bm_from_obj,
    create_mesh,
    create_object,
    calc_verts_median
    )


class BTOOLS_OT_test_window(bpy.types.Operator):
    """ Test creation of building windows """

    bl_idname = "btools.test_window"
    bl_label = "Test Window"

    collection_name = "test_window"
    props: bpy.props.PointerProperty(type=WindowProperty)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        # -- remove objects if any
        test_col = bpy.context.scene.collection.children.get(self.collection_name)
        if len(test_col.objects):
            list(map(bpy.data.meshes.remove, [ob.data for ob in test_col.objects]))
            list(map(bpy.data.objects.remove, test_col.objects))

        random_window(self, context, test_col)
        return {"FINISHED"}


def random_window(self, context, collection):
    types = list(map(op.itemgetter(0), self.props.fill_items))
    start_position = Vector((-7.5, 0, 2))

    for idx, wtype in enumerate(types):
        self.props.fill_type = wtype

        # -- default window
        randomize_props(self.props)
        default_window(self, context, collection, idx, start_position)

        # -- arch window
        randomize_props(self.props)
        arched_window(self, context, collection, idx, start_position)

        # -- array window
        randomize_props(self.props)
        array_window(self, context, collection, idx, start_position)

    # -- exclude all other collections apart from test_col from view layer
    for layer_col in bpy.context.view_layer.layer_collection.children:
        layer_col.exclude = not (layer_col.name == collection.name)


def randomize_props(props):
    if props.fill_type == 'NONE':
        pass

    elif props.fill_type == 'LOUVER':
        props.louver_fill.louver_count = random.randrange(5, 12)

    elif props.fill_type == 'BAR':
        props.bar_fill.bar_count_x = random.randrange(1, 4)
        props.bar_fill.bar_count_y = random.randrange(1, 4)

    elif props.fill_type == 'GLASS PANES':
        props.glass_fill.pane_count_x = random.randrange(1, 4)
        props.glass_fill.pane_count_y = random.randrange(1, 4)


def default_window(self, context, collection, idx, pos):
    position = pos + Vector((idx * 5, 0, 0))
    obj = create_window_plane(context, self.props, position)

    collection.objects.link(obj)
    obj.select_set(False)
    obj.show_wire = True


def arched_window(self, context, collection, idx, pos):
    self.props.arch.resolution = random.randrange(6, 16)
    self.props.arch.height = 1.0

    position = pos + Vector((idx * 5, 0, 5))
    obj = create_window_plane(context, self.props, position)

    collection.objects.link(obj)
    obj.select_set(False)
    obj.show_wire = True

    # --reset
    self.props.arch.resolution = 0


def array_window(self, context, collection, idx, pos):
    # XXX no point creating window without fill
    if idx == 0:
        return

    self.props.array.count = 3
    has_arch = random.random() > .5
    if has_arch:
        self.props.arch.resolution = random.randrange(6, 16)
        self.props.arch.height = 1.0

    position = pos + Vector((7.5, 0, 10 + ((idx-1) * 5)))
    obj = create_window_plane(context, self.props, position, size=(5, 2))

    collection.objects.link(obj)
    obj.select_set(False)
    obj.show_wire = True

    # --reset
    self.props.array.count = 0
    if has_arch:
        self.props.arch.resolution = 0


def create_window_plane(context, props, position, size=(2, 2)):
    name = "test_window_" + props.fill_type.lower()
    name += ('_arched' if props.arch.resolution > 0 else '')
    name += ('_array' if size[0] > 2 else '')

    obj = create_object(name, create_mesh(f"{name}_mesh"))
    bm = bm_from_obj(obj)

    plane(bm, *size)
    bmesh.ops.rotate(
        bm, verts=bm.verts,
        cent=calc_verts_median(bm.verts),
        matrix=Matrix.Rotation(math.pi/2, 4, 'X'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=position)
    create_window(bm, list(bm.faces), props)
    bm_to_obj(bm, obj)
    return obj