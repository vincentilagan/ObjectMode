bl_info = {
    "name": "Object Mode v1.2",
    "author": "Vincent Ilagan",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "Object Mode",
    "description": "Cinema 4D–style hierarchy selection with uniform world-space transforms",
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty

addon_keymaps = []

class OBJECT_OT_object_mode_hierarchy_select_v1_2(bpy.types.Operator):
    bl_idname = "object.object_mode_hierarchy_select_v1_2"
    bl_label = "Object Mode Hierarchy Select v1.2"
    bl_description = "Hold O and click to select parent + children with uniform transform"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        # Left click while holding O
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            obj = context.object
            if not obj:
                return {'RUNNING_MODAL'}

            # Store previous proportional editing state
            self.prev_prop = context.scene.tool_settings.use_proportional_edit_objects
            context.scene.tool_settings.use_proportional_edit_objects = False

            # Deselect all first
            bpy.ops.object.select_all(action='DESELECT')

            # Find top parent
            root = obj
            while root.parent:
                root = root.parent

            # Select parent + children
            root.select_set(True)
            for child in root.children_recursive:
                child.select_set(True)

            context.view_layer.objects.active = root

            # Store initial world locations for uniform movement
            self.initial_matrices = {o: o.matrix_world.copy() for o in context.selected_objects}

            return {'RUNNING_MODAL'}

        # Release O → exit modal and restore proportional editing
        if event.type == 'O' and event.value == 'RELEASE':
            context.scene.tool_settings.use_proportional_edit_objects = getattr(self, 'prev_prop', False)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.mode != 'OBJECT':
            self.report({'WARNING'}, "Object Mode only")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(OBJECT_OT_object_mode_hierarchy_select_v1_2)

    # Keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(
            OBJECT_OT_object_mode_hierarchy_select_v1_2.bl_idname,
            type='O',
            value='PRESS'
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(OBJECT_OT_object_mode_hierarchy_select_v1_2)


if __name__ == "__main__":
    register()
