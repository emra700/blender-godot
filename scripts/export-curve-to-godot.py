import bpy
from mathutils import Matrix, Vector, Euler

curvepath_template = """
[gd_resource type="Curve3D" format=2]

[resource]
_data = {
"points": PoolVector3Array( %s ),
"tilts": PoolRealArray( %s )
}
"""



def scale_vec(vec, scale):
    vec.x = vec.x*scale
    vec.y = vec.y*scale
    vec.z = vec.z*scale
    return vec

def makecurve(vec):
    vector3_template = """, %f, %f, %f"""
    res = ''
    res = res + vector3_template % (vec.x, vec.y, vec.z)
    return res


def makecurve_first(vec):
    vector3_template_first = """ %f, %f, %f"""
    vector3_string = ''
    vector3_string = vector3_string + vector3_template_first % (vec.x, vec.y, vec.z)        
    return vector3_string



def save_file(path, value):
     # Write data
    with open(path, "w") as file:
        file.write(value)   
    return {'FINISHED'}


def do_poly(spline, scale):
    curves = []
    tilts = []


    first = True
    
    for x in range(len(spline.points)):
        vec_point = spline.points[x].co

        vec_point = scale_vec(vec_point,scale)
        vec_handle_left = Vector((0.0, 0.0, 0.0))
        vec_handle_right = Vector((0.0, 0.0, 0.0))
            

        if first:
            curves.append( makecurve_first(vec_handle_right))
            curves.append( makecurve(vec_handle_left))            
            curves.append( makecurve(vec_point))
            tilts.append("0 ")
            first = False                
        else:
            curves.append( makecurve(vec_handle_right))
            curves.append( makecurve(vec_handle_left))            
            curves.append( makecurve(vec_point))
            tilts.append(",0 ")

    output = curvepath_template % (''.join(curves), ''.join(tilts))
    return output
    
def do_bez(spline, scale):
    curves = []
    tilts = []


    
    first = True
    
    for x in range(len(spline.bezier_points)):
        vec_point = spline.bezier_points[x].co
        vec_handle_left = vec_point - spline.bezier_points[x].handle_left
        vec_handle_right = vec_point - spline.bezier_points[x].handle_right

        vec_point = scale_vec(vec_point,scale)
        vec_handle_left = scale_vec(vec_handle_left,scale)
        vec_handle_right = scale_vec(vec_handle_right,scale)
            

        if first:
            curves.append( makecurve_first(vec_handle_right))
            curves.append( makecurve(vec_handle_left))            
            curves.append( makecurve(vec_point))
            tilts.append("0 ")
            first = False                
        else:
            curves.append( makecurve(vec_handle_right))
            curves.append( makecurve(vec_handle_left))            
            curves.append( makecurve(vec_point))
            tilts.append(",0 ")

    output = curvepath_template % (''.join(curves), ''.join(tilts))
    return output
    


def do_it(object, scale):
    
    if object.type != 'CURVE':
        print("object is not a CURVE. object is: %s" % object.type)        
        return None

    
    for spline in object.data.splines:
        print("spline type: %s" % spline.type)
        if spline.type == "BEZIER":
            output = do_bez(spline, scale)
        else:
            output = do_poly(spline, scale)
    return output
    



# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import Operator

class ExportGodotCurve(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.godot_curve"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Curve to Godot"

    # ExportHelper mixin class uses this
    filename_ext = ".tres"

    filter_glob: StringProperty(
        default="*.tres",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    scale: IntProperty(
        name="Scale",
        description="Scale",
        default=1,
    )

    def execute(dialog, context):
        output = do_it(bpy.context.active_object, dialog.scale)
        print(output)
        if output == None:
            return {'FINISHED'} 

        return save_file(dialog.filepath, output)
        


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportGodotCurve.bl_idname, text="Godot Curve Export")

def register():
    bpy.utils.register_class(ExportGodotCurve)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportGodotCurve)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.godot_curve('INVOKE_DEFAULT')