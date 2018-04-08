import bpy
from bpy.props import (PointerProperty,
    CollectionProperty, IntProperty)

from .generic import SplitProperty

from .floor     import FloorOperator, FloorProperty
from .floorplan import FloorplanOperator, FloorplanProperty
from .door      import DoorOperator, DoorProperty
from .window    import WindowOperator, WindowProperty


# -- take care here -- ORDER MATTERS !!!
classes = [
    SplitProperty,

    FloorOperator , FloorProperty,
    FloorplanOperator, FloorplanProperty,
    DoorOperator, DoorProperty,
    WindowOperator, WindowProperty,
]


def register_core():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.active_op = None


def unregister_core():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.active_op
