bl_info = {
    "name": "_ Z.Pivot Point Switcher",
    "author": "Yame",
    "version": (1, 0, 2),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Switch Transform Pivot Points and assign Ctrl+Shift+Period shortcut",
    "category": "3D View",
}

import bpy
from bpy.app.translations import register as register_translation, unregister as unregister_translation

# ----------------------------------------------------
# Pivot Point 一覧
# ----------------------------------------------------
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
    bl_label = "Next Pivot Point"  # ←固定英語に戻す
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        tool = scene.tool_settings

        current = tool.transform_pivot_point

        checked_pivots = [p[0] for p in pivot_points if getattr(scene, f"pivot_{p[0]}", False)]
        if not checked_pivots:
            self.report({"WARNING"}, bpy.app.translations.pgettext("No checked Pivot Points"))
            return {'CANCELLED'}

        if current not in checked_pivots:
            next_pivot = checked_pivots[0]
        else:
            idx = checked_pivots.index(current)
            next_pivot = checked_pivots[(idx + 1) % len(checked_pivots)]

        tool.transform_pivot_point = next_pivot

        msg = bpy.app.translations.pgettext("Pivot Point changed to") + f" {next_pivot}"
        self.report({"INFO"}, msg)
        print(msg)
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
        tr = bpy.app.translations.pgettext  # ショートカット

        box = layout.box()
        box.label(text=tr("Pivot Points to Cycle"))

        icon_map = {
            "BOUNDING_BOX_CENTER": "PIVOT_BOUNDBOX",
            "MEDIAN_POINT": "PIVOT_MEDIAN",
            "CURSOR": "PIVOT_CURSOR",
            "INDIVIDUAL_ORIGINS": "PIVOT_INDIVIDUAL",
            "ACTIVE_ELEMENT": "PIVOT_ACTIVE",
        }

        for pivot, label, _ in pivot_points:
            box.prop(scene, f"pivot_{pivot}", text=tr(label), icon=icon_map.get(pivot, 'NONE'))

        layout.separator()
        layout.operator("view3d.pivot_next_point", text=tr("Next Pivot Point"))

        layout.separator()
        layout.label(text=tr("Set Shortcut"))
        layout.operator("pivot.register_shortcut", text=tr("[Ctrl+Shift+.]"))

# ----------------------------------------------------
# ショートカット登録
# ----------------------------------------------------
class PIVOT_OT_register_shortcut(bpy.types.Operator):
    bl_idname = "pivot.register_shortcut"
    bl_label = "Register Ctrl+Shift+Period Shortcut"

    def execute(self, context):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps.get("3D View", None)

        if km:
            for kmi in list(km.keymap_items):
                if (kmi.idname == "view3d.pivot_next_point" and
                    kmi.type == 'PERIOD' and kmi.ctrl and kmi.shift and not kmi.alt):
                    km.keymap_items.remove(kmi)
            km.keymap_items.new("view3d.pivot_next_point", 'PERIOD', 'PRESS', ctrl=True, shift=True)
            self.report({"INFO"}, "Registered Ctrl+Shift+Period for Pivot Switch")
        else:
            self.report({"WARNING"}, "3D View keymap not found")
        return {'FINISHED'}

# ----------------------------------------------------
# 翻訳辞書
# ----------------------------------------------------
translation_dict = {
    "ja_JP": {
        ("*", "Pivot Point Switcher"): "ピボットポイント切り替え",
        ("*", "Pivot Points to Cycle"): "切り替え対象ピボット",
        ("*", "Next Pivot Point"): "次のピボットポイントへ",
        ("*", "Set Shortcut"): "ショートカット設定",
        ("*", "[Ctrl+Shift+.]"): "[Ctrl+Shift+.] 登録",
        ("*", "Register Ctrl+Shift+Period Shortcut"): "Ctrl+Shift+. を登録",
        ("*", "Registered Ctrl+Shift+Period for Pivot Switch"): "Ctrl+Shift+. にピボット切り替えを登録しました",
        ("*", "3D View keymap not found"): "3Dビューのキーマップが見つかりません",
        ("*", "No checked Pivot Points"): "チェックされたピボットポイントがありません",
        ("*", "Pivot Point changed to"): "ピボットポイントを変更しました:",
        ("*", "Bounding Box Center"): "バウンディングボックスの中心",
        ("*", "3D Cursor"): "3Dカーソル",
        ("*", "Individual Origins"): "個別の原点",
        ("*", "Median Point"): "中央値",
        ("*", "Active Element"): "アクティブ要素",
    }
}

# ----------------------------------------------------
# 登録 / 解除
# ----------------------------------------------------
classes = [PIVOT_OT_next_point, PIVOT_OT_register_shortcut, PIVOT_PT_panel]

def register():
    init_properties()
    for cls in classes:
        bpy.utils.register_class(cls)
    register_translation(__name__, translation_dict)

def unregister():
    clear_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_translation(__name__)

if __name__ == "__main__":
    register()
