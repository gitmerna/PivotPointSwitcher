bl_info = {
    "name": "_ Z.Pivot Point Switcher",
    "author": "Yame",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Switch Transform Pivot Points and assign Ctrl+Shift+Period shortcut",
    "category": "3D View",
}

import bpy

# Pivot Point 一覧（Blender内部名, 表示名, 説明）
pivot_points = [
    ("BOUNDING_BOX_CENTER", "Bounding Box Center", ""),
    ("CURSOR", "3D Cursor", ""),
    ("INDIVIDUAL_ORIGINS", "Individual Origins", ""),
    ("MEDIAN_POINT", "Median Point", ""),
    ("ACTIVE_ELEMENT", "Active Element", ""),
]

# ----------------------------------------------------
# Scene プロパティ登録
# ----------------------------------------------------
def init_properties():
    for pivot, _, _ in pivot_points:
        setattr(bpy.types.Scene, f"pivot_{pivot}", bpy.props.BoolProperty(name=pivot, default=True))

def clear_properties():
    for pivot, _, _ in pivot_points:
        if hasattr(bpy.types.Scene, f"pivot_{pivot}"):
            delattr(bpy.types.Scene, f"pivot_{pivot}")

# ----------------------------------------------------
# Pivot Point 切り替えオペレーター
# ----------------------------------------------------
class PIVOT_OT_next_point(bpy.types.Operator):
    bl_idname = "view3d.pivot_next_point"
    bl_label = "Next Pivot Point"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        tool = scene.tool_settings

        # 現在のピボット
        current = tool.transform_pivot_point
        print("現在の Pivot Point:", current)

        # チェックされたピボット候補
        checked_pivots = [p[0] for p in pivot_points if getattr(scene, f"pivot_{p[0]}", False)]
        if not checked_pivots:
            self.report({"WARNING"}, "チェックされた Pivot Point がありません")
            return {'CANCELLED'}

        # 次のピボットを決定
        if current not in checked_pivots:
            next_pivot = checked_pivots[0]
        else:
            idx = checked_pivots.index(current)
            next_pivot = checked_pivots[(idx + 1) % len(checked_pivots)]

        # 切り替え実行
        tool.transform_pivot_point = next_pivot

        self.report({"INFO"}, f"Pivot Point を {next_pivot} に変更")
        print(f"Pivot Point を {next_pivot} に変更")
        return {'FINISHED'}

# ----------------------------------------------------
# Ctrl+Shift+ピリオド で登録
# ----------------------------------------------------
class PIVOT_OT_register_shortcut(bpy.types.Operator):
    bl_idname = "pivot.register_shortcut"
    bl_label = "Register Ctrl+Shift+Period Shortcut"

    def execute(self, context):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        print("=== Ctrl+Shift+Period の登録処理 ===")

        km = kc.keymaps.get("3D View", None)
        if km:
            # 既存を削除
            for kmi in list(km.keymap_items):
                if (kmi.idname == "view3d.pivot_next_point" and
                    kmi.type == 'PERIOD' and kmi.ctrl and kmi.shift and not kmi.alt):
                    km.keymap_items.remove(kmi)
            # 新規登録
            kmi = km.keymap_items.new("view3d.pivot_next_point", 'PERIOD', 'PRESS', ctrl=True, shift=True)
            print("Ctrl+Shift+Period に view3d.pivot_next_point を登録しました。")
            self.report({"INFO"}, "Ctrl+Shift+Period に Pivot Next Point を登録しました")
        else:
            print("⚠ 3D View キーマップが見つかりませんでした。")
            self.report({"WARNING"}, "3D View キーマップが見つかりません")

        return {'FINISHED'}

# ----------------------------------------------------
# UI パネル
# ----------------------------------------------------
class PIVOT_PT_panel(bpy.types.Panel):
    bl_label = "Pivot Point Switcher"
    bl_idname = "PIVOT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="切り替えする対象")

        icon_map = {
            "BOUNDING_BOX_CENTER": "PIVOT_BOUNDBOX",
            "MEDIAN_POINT": "PIVOT_MEDIAN",
            "CURSOR": "PIVOT_CURSOR",
            "INDIVIDUAL_ORIGINS": "PIVOT_INDIVIDUAL",
            "ACTIVE_ELEMENT": "PIVOT_ACTIVE",
        }

        for pivot, label, _ in pivot_points:
            box.prop(scene, f"pivot_{pivot}", text=label, icon=icon_map.get(pivot, 'NONE'))

        layout.separator()
        layout.operator("view3d.pivot_next_point", text="Next Pivot Point")

        layout.separator()
        layout.operator("pivot.register_shortcut", text="Register Ctrl+Shift+Period")

# ----------------------------------------------------
# 登録 / 解除
# ----------------------------------------------------
classes = [PIVOT_OT_next_point, PIVOT_OT_register_shortcut, PIVOT_PT_panel]

def register():
    init_properties()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    clear_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
