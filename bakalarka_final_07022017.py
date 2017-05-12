bl_info = {
    "name": "Fracture",
    "author": "Lukáš Danko",
    "version": (1,0),
    "blender":(2,76,0),
    "location": "VIEW_3D > Tools > Fracture",
    "description":"fracture into cube,self,sphere,block,random,explosive ready",
    "warning":"",
    "wiki_url": "",
    "tracker_url":"",
    "category":"Object"}

## informacie o addone
import bpy
import bmesh
import math
import random
from bpy.types import Operator,Panel
from bpy.props import IntProperty, BoolProperty,EnumProperty,FloatProperty


class FracturePanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Fracture"

    @classmethod
    def poll(cls, context):
        if (context.active_object is not None):
            return context.active_object.type == "MESH"
        else:
            return False


class Create_basic_fracture(FracturePanel,Panel):
    bl_idname = "object.basic_fracture"
    bl_label = "Create basic Fracture"


    bpy.types.Object.pieces = IntProperty(
           name="subdivide",
           default=5,
           min=2,
           max = 10)


    bpy.types.Object.type_p = EnumProperty(items= (('0', 'Cube', 'Cubes'),
                                                 ('1', 'Block', 'Blocks'),
                                                 ('2', 'Sphere', 'Spheres'),
                                                 ('3', 'Self', 'Copies')),
                                                 name = "choose fracture type")
    bpy.types.Object.bomb = BoolProperty(name = "Explosive Ready")
    bpy.types.Object.delete = BoolProperty(name = "Keep original mesh")


    ## GUI rozlozenie
    def draw(self,context):
        ob = context.object
        layout = self.layout
        row = layout.row()
        row.prop(ob,"pieces")
        row = layout.row()
        row.prop(ob,"type_p")
        row = layout.row()
        row.prop(ob,"bomb")
        row = layout.row()
        row.prop(ob,"delete")
        row = layout.row()
        row.operator(Make_basic_Fracture.bl_idname)


class Make_basic_Fracture(Operator):
    bl_label = "Create"
    bl_idname = "make.basic_fract"
    def execute(self,context):

        ################## BASIC OBJECT INFO ######################
        all_properties = get_basic_info(True)
        default_object = all_properties[0]
        copy_object = all_properties[1]
        position = all_properties[2]
        dimensions = all_properties[3]
        rotation = all_properties[4]
        pieces = all_properties[5]

        #################### EXPLODE ###########################
        if default_object.bomb == True:
           explode(copy_object,position,dimensions,pieces,default_object.type_p)
           if not default_object.delete:
               delete_default_object(default_object)
           copy_object.dimensions = (dimensions[0] - 2, dimensions[1] - 2, dimensions[2] - 2)
           intersection_separate(copy_object, rotation)
           bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
           return {"FINISHED"}

        ################# BASIC SHADES ###########################
        if default_object.type_p=="0":
                create_cubes(position,dimensions,pieces)
        elif default_object.type_p=="1":
                create_fract(position,dimensions,pieces)

        elif default_object.type_p=="2":
                create_sphere(position,dimensions,pieces)

        elif default_object.type_p=="3":
                create_duply(position,dimensions,pieces)

        if not default_object.delete:
            delete_default_object(default_object)
        copy_object.dimensions = (dimensions[0]-2,dimensions[1]-2,dimensions[2]-2)
        intersection_separate(copy_object, rotation)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {"FINISHED"}


class Create_random_fracture(FracturePanel,Panel):
    bl_idname = "object.random_fracture"
    bl_label = "Create random Fracture"


    bpy.types.Object.delete = BoolProperty(name="Keep original mesh")
    bpy.types.Object.test = BoolProperty(name="Test")
    bpy.types.Object.planeH = IntProperty(
           name="planeH",
           default=45,
           min=0,
           max = 90)
    bpy.types.Object.planeV = IntProperty(
           name="planeV",
           default=45,
           min=0,
           max = 90)
    bpy.types.Object.planeVR = IntProperty(
           name="planeVR",
           default=45,
           min=0,
           max = 90)
    bpy.types.Object.discrepancy_X = FloatProperty(
           name="discrepancy_X",
           default=0.50,
           min=0.00,
           max = 1.00)
    bpy.types.Object.discrepancy_Y = FloatProperty(
           name="discrepancy_Y",
           default=0.50,
           min=0.00,
           max = 1.00)
    bpy.types.Object.discrepancy_Z = FloatProperty(
           name="discrepancy_Z",
           default=0.50,
           min=0.00,
           max = 1.00)
    bpy.types.Object.one = IntProperty(
        name="subdivide",
        default=1,
        min=1,
        max=2)
    bpy.types.Object.two = IntProperty(
        name="subdivide",
        default=1,
        min=1,
        max=2)
    bpy.types.Object.three = IntProperty(
        name="subdivide",
        default=1,
        min=1,
        max=2)
    bpy.types.Object.grid_type = EnumProperty(items=(('0', 'grid', '9x9'),
                                                  ('1', 'custom', 'custom grid')),
                                           name="choose grid system")
    bpy.types.Object.x = bpy.props.BoolProperty(name ="X")
    bpy.types.Object.y = bpy.props.BoolProperty(name ="Y")
    bpy.types.Object.z = bpy.props.BoolProperty(name ="Z")


    ## GUI rozlozenie
    def draw(self, context):
        ob = context.object
        layout = self.layout

        row = layout.row()
        row.prop(ob,"grid_type")
        row = layout.row()
        row.prop(ob,"discrepancy_X")
        row = layout.row()
        row.prop(ob,"discrepancy_Y")
        row = layout.row()
        row.prop(ob,"discrepancy_Z")
        row = layout.row()
        row.prop(ob,"planeH")
        row = layout.row()
        row.prop(ob,"planeV")
        row = layout.row()
        row.prop(ob,"planeVR")
        row = layout.row()
        row.prop(ob, "delete")
        row = layout.row()
        row.prop(ob, "x")
        row = layout.row()
        row.prop(ob, "y")
        row = layout.row()
        row.prop(ob, "z")
        rowOne = layout.row()
        rowOne.prop(ob, "one")
        rowTwo = layout.row()
        rowTwo.prop(ob, "two")
        rowThree = layout.row()
        rowThree.prop(ob, "three")
        if ob.grid_type == '0':
            rowOne.enabled = False
            rowTwo.enabled = False
            rowThree.enabled = False
        row = layout.row()

        row.operator(Make_random_Fracture.bl_idname)

class Make_random_Fracture(Operator):
        bl_label = "Create"
        bl_idname = "make.random_fract"

        def execute(self, context):
            all_properties = get_basic_info()
            default_object = all_properties[0]
            copy_object = all_properties[1]
            position = all_properties[2]
            dimensions = all_properties[3]
            rotation = all_properties[4]
            axis = [default_object.x,default_object.y,default_object.z]
            if default_object.grid_type == '0':
                 create_temp_grid_random(position,dimensions)
                 delete_mesh()
                 array_co = discrepancy(dimensions, default_object.discrepancy_X, default_object.discrepancy_Y, default_object.discrepancy_Z, True, [3,3,8])
            else:
                make_points(position,default_object.one,default_object.two,default_object.three)
                array_co = discrepancy(dimensions, default_object.discrepancy_X, default_object.discrepancy_Y, default_object.discrepancy_Z, False, axis)
            make_planes(array_co,dimensions,copy_object,default_object.planeH,default_object.planeV,default_object.planeVR,axis)
            # bpy.data.objects['FractureMash_duplicate'].dimensions = dimensions_original
            if not default_object.delete:
                delete_default_object(default_object)

            copy_object.rotation_euler = rotation
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['temp_grid'].select = True
            bpy.ops.object.delete()
            copy_object.dimensions = (dimensions[0] - 2, dimensions[1] - 2, dimensions[2] - 2)
            separate_loose(copy_object)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            return {"FINISHED"}



##################################### OBJEKTY ############################

def properties_object(dim,pieces):
    axis = min(dim[0],dim[1],dim[2])
    cube_size = (axis/pieces)/2
    return [axis,cube_size]


def object_name(axis,pieces,dim,number ,name,inner):
    fract = bpy.context.active_object
    fract.name = name
    if name == "temp_grip":
        fract.dimensions =(axis/pieces,axis/pieces,0)
        create_count(pieces,dim,axis,fract,number,name,inner)
    fract.dimensions =(axis/pieces,axis/pieces,axis/pieces)
    create_count(pieces,dim,axis,fract,number,name,inner)


#vytvory maly kvader
def create_fract(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    cube_size_x = (dim[0]/pieces)/2
    cube_size_y = (dim[1]/pieces)/2
    cube_size_z = (dim[2]/pieces)/2
    bpy.ops.mesh.primitive_cube_add(view_align=False, location=(pos[0]-(dim[0]/2)+cube_size_x,pos[1]-(dim[1]/2)+cube_size_y,pos[2]-(dim[2]/2)+cube_size_z))
    fract = bpy.context.active_object
    fract.dimensions =(dim[0]/pieces,dim[1]/pieces,dim[2]/pieces)
    fract.name = name
    axis = 1
    create_count1(pieces,dim,axis,fract,1.004,name,inner)


#vytvory malu kocku
def create_cubes(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    props = properties_object(dim,pieces)
    bpy.ops.mesh.primitive_cube_add(location=((pos[0]-dim[0]/2)+props[1],(pos[1]-dim[1]/2)+props[1],(pos[2]-dim[2]/2)+props[1]))
    object_name(props[0],pieces,dim,1.004,name,inner)


## grip pre random
def create_temp_grid_random(pos,dim):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions  = 3,y_subdivisions  = 3,location=(pos[0],pos[1],pos[2]))
    fract = bpy.context.active_object
    fract.name = "temp_grid"
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))


#vytvory malu gulu
def create_sphere(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    props = properties_object(dim,pieces)
    bpy.ops.mesh.primitive_ico_sphere_add(location=((pos[0]-dim[0]/2)+ props[1],(pos[1]-dim[1]/2)+props[1],(pos[2]-dim[2]/2)+props[1]))
    object_name(props[0],pieces,dim,1.004,name,inner)


#vytvory malu kopiu
def create_duply(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    axis = min(dim[0],dim[1],dim[2])
    cube_size = (axis/pieces)/2
    me = bpy.data.objects["FractureMash_Default"].data
    me_copy = me.copy()
    fract = bpy.data.objects.new("FractureOnePartMesh", me_copy)
    fract.dimensions =(axis/pieces,axis/pieces,axis/pieces)
    fract.location=((pos[0]-dim[0]/2)+cube_size,(pos[1]-dim[1]/2)+cube_size,(pos[2]-dim[2]/2)+cube_size)
    scene = bpy.context.scene
    scene.objects.link(fract)
    scene.update()
    create_count(pieces,dim,axis,fract,1.004,name,inner)

def make_points(location,u,v,w):
    EPS = 1e-10

    def my_range(start, stop, step):
        r = start
        while r < stop:
            yield r
            r += step

    delta_x = 2.0 / (u + 1)
    delta_y = 2.0 / (v + 1)
    delta_z = 2.0 / (w + 1)

    points = []
    for x in my_range(-1.0 + delta_x, 1.0 - delta_x + EPS, delta_x):
        for y in my_range(-1.0 + delta_y, 1.0 - delta_y + EPS, delta_y):
            for z in my_range(-1.0 + delta_z, 1.0 - delta_z + EPS, delta_z):
                points.append((x, y, z))


    bpy.ops.object.add(
        type='MESH',
        enter_editmode=False,
        location=location)
    ob = bpy.context.object
    ob.name = 'temp_grid'
    ob.show_name = True
    me = ob.data
    me.name = 'temp_grid'

    # Create mesh from given verts, faces.
    me.from_pydata(points, [], [])
    # Update mesh with new data
    me.update()
    # Set object mode
    bpy.ops.object.editmode_toggle()



######################################## MODIFIKATORY #################################################################

#array modifikator
def array(obj,count,axis,number):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_add(type='ARRAY')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].count = count
    bpy.context.object.modifiers["{name}".format(name=c_name)].use_relative_offset = True
    bpy.context.object.modifiers["{name}".format(name=c_name)].relative_offset_displace[0] = 0
    bpy.context.object.modifiers["{name}".format(name=c_name)].relative_offset_displace[axis] = number
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Array')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

#vytvara prienik dvoch ojektov
def make_intersection(obj,rot):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_add(type='BOOLEAN')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].operation = 'INTERSECT'
    bpy.context.object.modifiers["{name}".format(name=c_name)].object = bpy.data.objects["{next_n}".format(next_n = bpy.data.objects["FractureOnePartMesh"].name)]
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Boolean')
    obj.rotation_euler = rot
    bpy.data.objects['FractureOnePartMesh'].select = True
    obj.select = False
    bpy.ops.object.delete()

#rozdiel dvoch objektov
def make_difference(obj,name = "FractureOnePartMesh"):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.modifier_add(type='BOOLEAN')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["{name}".format(name=c_name)].object = bpy.data.objects["{next_n}".format(next_n = bpy.data.objects[name].name)]
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Boolean')
    bpy.data.objects[name].select = True
    obj.select = False
    bpy.ops.object.delete()

def solidify():
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].thickness = 0.003
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Solidify')



################################## ROZDELENIE OBJEKTOV ###############################

## rozdelenie na male casti
def separate_loose(ob):
    bpy.data.objects[ob.name].select = True
    bpy.ops.mesh.separate(type="LOOSE")

#vytvara diery do objektu
def differ(obj,pos,dime,count,i):
    temp_dimensions = [None,None,None]
    #vytvorim a pomenujem kocku
    bpy.ops.mesh.primitive_cube_add(location=(pos[0],pos[1],pos[2]))
    dif = bpy.context.active_object
    dif.name = "differ"

    ## ta 0.005 by bolo fajn ratat nejaky scale parametrom,  12.5 zvacime objekt o base dimenensiu [dom[i] +2 ]
    dif.dimensions = (dime[0]-((dime[0]/count)*(2*i)-0.05),dime[1]-((dime[1]/count)*(2*i)-0.05),dime[2]-((dime[2]/count)*(2*i)-0.05))
    bpy.context.scene.update()
    temp_dimensions[0] = bpy.data.objects['differ'].dimensions[0] - 0.05
    temp_dimensions[1] = bpy.data.objects['differ'].dimensions[1] - 0.05
    temp_dimensions[2] = bpy.data.objects['differ'].dimensions[2] - 0.05
    bpy.ops.object.select_all(action='DESELECT')
    dif.select = True
    make_difference(obj,dif.name)
    position = dif.location
    # make_intersection(dif,(0,0,0))
    return [position,temp_dimensions]

def plane_differ(plane,ob):
    plane.name = "FractureMeshPlane"
    make_difference()
    bpy.data.objects['FFplane'].select = True
    ob.select = False
    bpy.ops.object.delete()




############### POMOCNE FUNKCIE #######################

#skopiruje objekt
def copy_selected_object():
     main = bpy.context.active_object
     bpy.ops.object.duplicate()
     ob = bpy.context.active_object
     return main,ob


#property objektu
def properties(Meshobject):
    return [Meshobject.location,Meshobject.dimensions,Meshobject.rotation_euler[:],Meshobject.pieces]

#prienik a rozdelenie objektu
def intersection_separate(default_object,rotation):
    make_intersection(default_object,rotation)
    separate_loose(default_object)


#pocet malych objektov
def create_count(pieces,dim,axis,cube,number,name,inner):
    array(cube,math.ceil(pieces*(dim[0]/axis))-inner,0,number)
    array(cube,math.ceil(pieces*(dim[1]/axis))-inner,1,number)
    if name != 'temp_grip':
        array(cube,math.ceil(pieces*(dim[2]/axis))-inner,2,number)

# zvlast metoda pre block
def create_count1(pieces,dim,axis,cube,number,name,inner):
    array(cube,math.ceil(pieces-inner),0,number)
    array(cube,math.ceil(pieces-inner),1,number)
    if name != 'temp_grip':
        array(cube,math.ceil(pieces-inner),2,number)


def delete_mesh():
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.delete(type="EDGE_FACE")


### roztrasenie bodov
def discrepancy(main_object_dimension, discrepancyX, discrepancyY, discrepancyZ,tempZ, axis):
    ob = bpy.data.objects['temp_grid']
    mesh=bmesh.from_edit_mesh(bpy.context.object.data)
    if tempZ:
        temp_z = main_object_dimension[2]/2 - main_object_dimension[2]/(axis[2] +1)
    else:
        temp_z = 0
    for v in mesh.verts:
            v.co = (random_co(v.co[0],main_object_dimension[0]/(axis[0]+1),discrepancyX),random_co(v.co[1],main_object_dimension[1]/(axis[1] + 1),discrepancyY),random_co(v.co[2] + temp_z,main_object_dimension[2]/(axis[2] +1),discrepancyZ))
            if tempZ:
                temp_z -= main_object_dimension[2]/(axis[2] +1)
    final_co_array = [ob.matrix_world * vert.co for vert in mesh.verts]
    # trigger viewport update
    bpy.context.scene.objects.active = bpy.context.scene.objects.active
    bpy.ops.object.mode_set(mode='OBJECT')
    return final_co_array


def random_co(coordinate, dimenzion,discrepancy):
    return  coordinate + random.uniform(-dimenzion*discrepancy,dimenzion*discrepancy)


def random_angle(angle,dicrepancy):
    return math.pi/180 * ( angle + random.uniform(-dicrepancy,dicrepancy))


def make_planes(array_co,dimension,obj,horizont, vertical,vertical_rot,axis):
    for v in array_co:
        if axis[0]:
            define_plane(dimension,v)
            bpy.ops.transform.rotate(value=random_angle(90, vertical), axis=(0, 1, 0))
            solidify()
            make_difference(obj)
        if axis[1]:
            define_plane(dimension, v)
            bpy.ops.transform.rotate(value=random_angle(90, vertical_rot), axis=(1, 0, 0))
            solidify()
            make_difference(obj)
        if axis[2]:
            define_plane(dimension, v)
            bpy.ops.transform.rotate(value=random_angle(0, horizont), axis=(1, 0, 0))
            solidify()
            make_difference(obj)



    # group()
    # make_difference(obj)

def define_plane(dimension,v):
    bpy.ops.mesh.primitive_plane_add(location=(v[0], v[1], v[2]))
    plane = bpy.context.active_object
    plane.name = "FractureOnePartMesh"
    plane.dimensions = (dimension[0] * 3, dimension[1] * 3, 0)

# ##oznacenie vsetkych novo vytvorench objektov
def group(name = "FractureOnePartMesh", scale = 1.01):
    for ob in bpy.context.scene.objects:
        if name in ob.name:
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
    bpy.ops.object.join()
    all = bpy.context.active_object
    all.name = name
    bpy.ops.transform.resize(value=(scale,scale,scale))


#urcenie typu objektu
def types(typ,position,dimensions,pieces,name,inner = False):
    if typ =="0":
        create_cubes(position,dimensions,pieces,name,inner)
    elif typ =="1":
        create_fract(position,dimensions,pieces,name,inner)
    elif typ == "2":
        create_sphere(position,dimensions,pieces,name,inner)
    elif typ == "3":
        create_duply(position,dimensions,pieces,name,inner)
########################## PRIDANIE EXPLOZIE ###################


def explode(ob,pos,dime,pieces,typ):
    ## count je pocet "rozdeleni"
    ## n je pocet deleni
    count = pieces//2
    if count%2==0:
        n = count//2
    else:
        n = count//2+1
    inr=2
    k=1
    ## tu sa mi vyvoria "kocky"
    types(typ,pos,dime,count,"FractureOnePartMesh_0")
    ob = bpy.context.active_object
    for i in range(n):
        if i!=n-1:
            ## param: povodnu objekt , pozicia ,dimenzia , pocet casti , i+1 , nieco brutalne , typ
            pos_dim = differ(ob,pos,dime,count,i+1)

            pieces = (count-inr)*(2**k)
            minimal = min(pos_dim[1][0],pos_dim[1][1],pos_dim[1][2])
            if(pos_dim[1][0] < math.ceil(pieces*(pos_dim[1][0]/minimal)) * (minimal/pieces)
                or pos_dim[1][1] < math.ceil(pieces*(pos_dim[1][1]/minimal)) * (minimal/pieces)
               or pos_dim[1][2] < math.ceil(pieces*(pos_dim[1][2]/minimal)) * (minimal/pieces)):
                types(typ, pos_dim[0], pos_dim[1], ((count-inr)*(2**k)),"FractureOnePartMesh_" + str(i+1),True)
            else:
                types(typ, pos_dim[0], pos_dim[1], (count-inr)*(2**k),"FractureOnePartMesh_" + str(i+1))
            # raise Exception()
            ob = bpy.context.active_object
        inr+=2

        k+=1
    group()


def delete_default_object(default_object):
    bpy.ops.object.select_all(action='DESELECT')
    default_object.select = True
    bpy.ops.object.delete()

def get_basic_info(all = False):
    default_object, copy_object = copy_selected_object()
    default_object.name = "FractureMash_Default"
    copy_object.name = "FractureMash_duplicate"
    position = properties(default_object)[0]
    dimensions = properties(default_object)[1]
    dimensions = (dimensions[0]+2,dimensions[1]+2,dimensions[2]+2)
    # dimensions = (dimensions_original[0]*2,dimensions_original[1]*2,dimensions_original[2]*2)
    rotation = properties(default_object)[2]
    if all:
        pieces = properties(default_object)[3]
    else:
        pieces = None
    copy_object.rotation_euler = (0, 0, 0)
    copy_object.dimensions = dimensions

    return [default_object,copy_object,position,dimensions,rotation,pieces]



def register():
    bpy.utils.register_class(Create_basic_fracture)
    bpy.utils.register_class(Create_random_fracture)
    bpy.utils.register_class(Make_basic_Fracture)
    bpy.utils.register_class(Make_random_Fracture)


def unregister():
    bpy.utils.unregister_class(Create_basic_fracture)
    bpy.utils.unregister_class(Create_random_fracture)
    bpy.utils.unregister_class(Make_basic_Fracture)
    bpy.utils.unregister_class(Make_random_Fracture)


if __name__ == "__main__":
    register()



############################################# PANEL
 # bpy.types.Object.planeH = IntProperty(
    #        name="planeH",
    #        default=45,
    #        min=0,
    #        max = 90)
    # bpy.types.Object.planeV = IntProperty(
    #        name="planeV",
    #        default=45,
    #        min=0,
    #        max = 90)
    # bpy.types.Object.planeVR = IntProperty(
    #        name="planeVR",
    #        default=45,
    #        min=0,
    #        max = 90)
    # bpy.types.Object.discrepancy_X = FloatProperty(
    #        name="discrepancy_X",
    #        default=0.50,
    #        min=0.00,
    #        max = 1.00)
    # bpy.types.Object.discrepancy_Y = FloatProperty(
    #        name="discrepancy_Y",
    #        default=0.50,
    #        min=0.00,
    #        max = 1.00)
    # bpy.types.Object.discrepancy_Z = FloatProperty(
    #        name="discrepancy_Z",
    #        default=0.50,
    #        min=0.00,
    #        max = 1.00)
    ################################execute
# default_object,copy_object =  copy_selected_object()
# #nastevenie mien Meshov
# default_object.name = "FractureMash_Default"
# copy_object.name = "FractureMash_duplicate"
# #nastavenie vlastnosti
# position = properties(default_object)[0]
# dimensions = properties(default_object)[1]
# # dimensions = (dimensions_original[0]*2,dimensions_original[1]*2,dimensions_original[2]*2)
# rotation = properties(default_object)[2]
# pieces = properties(default_object)[3]
# copy_object.rotation_euler = (0,0,0)
# # default_object.rotation_euler = (0,0,0)
# # default_object.draw_bounds_type = "CAPSULE"
# copy_object.dimensions = dimensions
################################ type random
 # if default_object.type_p == "4":
        #         # create_temp_grid_random(position,dimensions,pieces)
        #         # delete_mesh()
        #         ob = make_points(position,1,1,1)
        #         array_co = discrepancy(dimensions, default_object.discrepancy_X, default_object.discrepancy_Y, default_object.discrepancy_Z)
        #         make_planes(array_co,dimensions,copy_object,default_object.planeH,default_object.planeV,default_object.planeVR)
        #         # bpy.data.objects['FractureMash_duplicate'].dimensions = dimensions_original
        #         if not default_object.delete:
        #             bpy.ops.object.select_all(action='DESELECT')
        #             default_object.select = True
        #             bpy.ops.object.delete()
        #
        #         copy_object.rotation_euler = rotation
        #         bpy.ops.object.select_all(action='DESELECT')
        #         bpy.data.objects['temp_grid'].select = True
        #         bpy.ops.object.delete()
        #         separate_loose(copy_object)
        #         bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        #         return {"FINISHED"}