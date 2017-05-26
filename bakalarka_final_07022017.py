
import bpy
import bmesh
import math
import random
from bpy.types import Operator,Panel
from bpy.props import IntProperty, BoolProperty,EnumProperty,FloatProperty


###################### META DATA #####################


bl_info = {
    "name": "Fracture",
    "author": "Lukáš Danko",
    "version": (1,0),
    "blender":(2,77,0),
    "location": "VIEW_3D > Tools > Fracture",
    "description":"fracture into cube,self,sphere,block,random,explosive ready",
    "warning":"",
    "wiki_url": "",
    "tracker_url":"",
    "category":"Object"}


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
           name="pieces",
           description = 'Number of pieces on smallest side of object',
           default=5,
           min=2,
           max = 10)
    bpy.types.Object.inner = IntProperty(
           name="explosive",
           description  = 'Number of inner to object',
           default=2,
           min=1,
           max = 3)


    bpy.types.Object.type_p = EnumProperty(items= (('0', 'Cube', 'Cubes'),
                                                 ('1', 'Block', 'Blocks'),
                                                 ('2', 'Sphere', 'Spheres'),
                                                 ('3', 'Self', 'Copies')),
                                                 name = "choose fracture type",
                                                description = 'choose type of object for fracture' )
    bpy.types.Object.bomb = BoolProperty(name = "Explosive Ready", description ='Create fracture with smaller fract in the middle of object' )
    bpy.types.Object.delete = BoolProperty(name = "Keep original mesh", description ='Choose if you want keep original object')



    ## GUI rozlozenie
    def draw(self,context):
        ob = context.object
        layout = self.layout
        layout.label('Set Fracture Number')
        row1 = layout.row()
        row1.prop(ob,"pieces")
        row2 = layout.row()
        row2.prop(ob,"inner")

        row = layout.row()
        row.prop(ob,"type_p")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(ob,"bomb")
        row.prop(ob,"delete")

        row = layout.row()
        row.operator(Make_basic_Fracture.bl_idname)
        if not ob.bomb:
            row2.enabled = False
        if ob.bomb:
            row1.enabled = False


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
           explode(position,dimensions,default_object.inner,default_object.type_p)
           if not default_object.delete:
               delete_default_object(default_object)

           intersection_separate(copy_object ,dimensions,rotation)
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


        ######################### SEPARATE #############################


        intersection_separate(copy_object,dimensions ,rotation)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {"FINISHED"}


class Create_random_fracture(FracturePanel,Panel):
    bl_idname = "object.random_fracture"
    bl_label = "Create random Fracture"

    bpy.types.Object.delete1 = BoolProperty(name="Keep original mesh",
                                            description='Choose if you want keep original object')
    bpy.types.Object.planeH = IntProperty(
           name="X",
           default=20,
           min=0,
           max = 45,
            description = 'rotate plane around axis X')
    bpy.types.Object.planeV = IntProperty(
           name="Y",
           default=20,
           min=0,
           max = 45,
        description='rotate plane around axis Y')
    bpy.types.Object.planeVR = IntProperty(
           name="Z",
           default=20,
           min=0,
           max = 45,
        description='rotate plane around axis Z')
    bpy.types.Object.discrepancy_X = FloatProperty(
           name="X",
           default=0.50,
           min=0.00,
           max = 1.00,
        description='jitter point in line X')
    bpy.types.Object.discrepancy_Y = FloatProperty(
           name="Y",
           default=0.50,
           min=0.00,
           max = 1.00,
        description='jitter point in line Y')
    bpy.types.Object.discrepancy_Z = FloatProperty(
           name="Z",
           default=0.50,
           min=0.00,
           max = 1.00,
        description='jitter point in line Z')
    bpy.types.Object.one = IntProperty(
        name="X",
        default=1,
        min=1,
        max=2,
        description='create point on line X')
    bpy.types.Object.two = IntProperty(
        name="Y",
        default=1,
        min=1,
        max=2,
        description='create point on line Y')
    bpy.types.Object.three = IntProperty(
        name="Z",
        default=1,
        min=1,
        max=2,
        description='create point on line Z')
    bpy.types.Object.grid_type = EnumProperty(items=(('0', 'grid', '9x9'),
                                                  ('1', 'custom', 'custom grid')),
                                           name="choose grid system",description='Choose system for generate points')
    bpy.types.Object.x = bpy.props.BoolProperty(name ="X", description='Create planes in line X')
    bpy.types.Object.y = bpy.props.BoolProperty(name ="Y",description='Create planes in line Y')
    bpy.types.Object.z = bpy.props.BoolProperty(name ="Z", description='Create planes in line Z')


    ## GUI rozlozenie
    def draw(self, context):
        ob = context.object
        layout = self.layout
        row = layout.row()
        row.prop(ob,"grid_type")

        layout.label("Jitter points")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(ob,"discrepancy_X")
        row.prop(ob,"discrepancy_Y")
        row.prop(ob,"discrepancy_Z")

        layout.label("Randomize angle")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(ob,"planeH")
        row.prop(ob,"planeV")
        row.prop(ob,"planeVR")

        layout.label("Number of points on Custom grid")
        rowPoints = layout.row(align=True)
        rowPoints.prop(ob, "one")
        rowPoints.prop(ob, "two")
        rowPoints.prop(ob, "three")

        layout.label("Make slide in axis")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(ob, "x")
        row.prop(ob, "y")
        row.prop(ob, "z")

        row = layout.row()
        row.prop(ob, "delete1")
        if ob.grid_type == '0':
            rowPoints.enabled = False
        row = layout.row()
        row.operator(Make_random_Fracture.bl_idname)


class Make_random_Fracture(Operator):
        bl_label = "Create"
        bl_idname = "make.random_fract"

        def execute(self, context):


            ##################### BASIC INFO #######################


            all_properties = get_basic_info()
            default_object = all_properties[0]
            copy_object = all_properties[1]
            position = all_properties[2]
            dimensions = all_properties[3]
            rotation = all_properties[4]
            axis = [default_object.x,default_object.y,default_object.z]


            ####################### GRID TYPE ###########################


            if default_object.grid_type == '0':
                 create_temp_grid_random(position,dimensions)
                 delete_mesh()
                 array_co = discrepancy(dimensions, default_object.discrepancy_X, default_object.discrepancy_Y, default_object.discrepancy_Z, True, [3,3,9])

            else:
                make_points(position, dimensions, default_object.one,default_object.two,default_object.three)
                array_co = discrepancy(dimensions, default_object.discrepancy_X, default_object.discrepancy_Y, default_object.discrepancy_Z, False, axis)



            ####################### SLIDES #######################


            jitter = [default_object.discrepancy_X,default_object.discrepancy_Y,default_object.discrepancy_Z]
            make_planes(array_co,dimensions,copy_object,default_object.planeH,default_object.planeV,default_object.planeVR,axis,jitter)
            if not default_object.delete:
                delete_default_object(default_object)

            ################################# SEPARATE #####################


            copy_object.rotation_euler = rotation
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['temp_grid'].select = True
            bpy.ops.object.delete()
            copy_object.dimensions = (dimensions[0] - 2, dimensions[1] - 2, dimensions[2] - 2)
            separate_loose(copy_object)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            return {"FINISHED"}


##################################### TVORBA BASIC OBJEKTOV ############################


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
    props = get_fract_size(dim, pieces)
    bpy.ops.mesh.primitive_cube_add(location=((pos[0]-dim[0]/2)+props[1],(pos[1]-dim[1]/2)+props[1],(pos[2]-dim[2]/2)+props[1]))
    set_fract_dimesion(props[0], pieces, dim, 1.004, name, inner)


#vytvory malu gulu
def create_sphere(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    props = get_fract_size(dim, pieces)
    bpy.ops.mesh.primitive_ico_sphere_add(location=((pos[0]-dim[0]/2)+ props[1],(pos[1]-dim[1]/2)+props[1],(pos[2]-dim[2]/2)+props[1]))
    set_fract_dimesion(props[0], pieces, dim, 1.004, name, inner)


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


################################### EXPOSIVE READY #################################


def explode(pos,dime,n,typ):
    count = (n*2) +1
    n += 1
    inr=2
    k=1
    types(typ,pos,dime,count,"FractureOnePartMesh_0")
    ob = bpy.context.active_object
    for i in range(n):
        if i!=n-1:
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


###################################### Udaje a pomcne funkcie pe objekty


# vrati pozicu dimenxiu atd
def get_basic_info(all = False):
    default_object, copy_object = copy_selected_object()
    default_object.name = "FractureMash_Default"
    copy_object.name = "FractureMash_duplicate"
    position = get_PDR(default_object)[0]
    dimensions = get_PDR(default_object)[1]
    dimensions = (dimensions[0]+2,dimensions[1]+2,dimensions[2]+2)
    copy_object.dimensions = dimensions
    rotation = get_PDR(default_object)[2]
    if all:
        pieces = get_PDR(default_object)[3]
    else:
        pieces = None
    copy_object.rotation_euler = (0, 0, 0)
    copy_object.dimensions = dimensions
    return [default_object,copy_object,position,dimensions,rotation,pieces]


#skopiruje objekt
def copy_selected_object():
     main = bpy.context.active_object
     bpy.ops.object.duplicate()
     ob = bpy.context.active_object
     return main,ob


#vypocita velkost maleho dielu
def get_fract_size(dim, pieces):
    axis = min(dim[0],dim[1],dim[2])
    cube_size = (axis/pieces)/2
    return [axis,cube_size]


#nastavi velkost a meno deliacemu objektu
def set_fract_dimesion(axis, pieces, dim, number, name, inner):
    fract = bpy.context.active_object
    fract.name = name
    fract.dimensions =(axis/pieces,axis/pieces,axis/pieces)
    create_count(pieces,dim,axis,fract,number,name,inner)


# vrati poziciu polohu atd (pomocna funcia pre get basic info)
def get_PDR(Meshobject):
    return [Meshobject.location,Meshobject.dimensions,Meshobject.rotation_euler[:],Meshobject.pieces]


#pocet malych objektov
def create_count(pieces,dim,axis,cube,number,name,inner):
    array(cube,math.ceil(pieces*(dim[0]/axis))-inner,0,number)
    array(cube,math.ceil(pieces*(dim[1]/axis))-inner,1,number)
    array(cube,math.ceil(pieces*(dim[2]/axis))-inner,2,number)


# zvlast metoda pre block
def create_count1(pieces,dim,axis,cube,number,name,inner):
    array(cube,math.ceil(pieces-inner),0,number)
    array(cube,math.ceil(pieces-inner),1,number)
    array(cube,math.ceil(pieces-inner),2,number)


# zmaze vsetko okrem vrcholov objekt potom ostava v edit mode
def delete_mesh():
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type="EDGE_FACE")


# ##oznacenie vsetkych novo vytvorench objektov a joinutie do jedneho objektu
def group(name="FractureOnePartMesh", scale=1.01):
    for ob in bpy.context.scene.objects:
        if name in ob.name:
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
    bpy.ops.object.join()
    all = bpy.context.active_object
    all.name = name
    bpy.ops.transform.resize(value=(scale, scale, scale))


# urcenie typu objektu pre expolosive
def types(typ, position, dimensions, pieces, name, inner=False):
    if typ == "0":
        create_cubes(position, dimensions, pieces, name, inner)
    elif typ == "1":
        create_fract(position, dimensions, pieces, name, inner)
    elif typ == "2":
        create_sphere(position, dimensions, pieces, name, inner)
    elif typ == "3":
        create_duply(position, dimensions, pieces, name, inner)


####################################### NADODNE DELENIE , BODY  #################################


## vytvori siet bodov 3x3
def create_temp_grid_random(pos, dim):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=3, y_subdivisions=3, location=(pos[0], pos[1], pos[2]),)
        fract = bpy.context.active_object
        fract.name = "temp_grid"
        fract.dimensions = dim
        bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))


## custom siet
def make_points(location, dimension,  u, v, w):
        EPS = 1e-10
        delta_x = dimension[0] / (u + 1)
        delta_y = dimension[1] / (v + 1)
        delta_z = dimension[2] / (w + 1)

        points = []
        for x in my_range(-(dimension[0]/2) + delta_x, (dimension[0]/2) - delta_x + EPS, delta_x):
            for y in my_range(-(dimension[1]/2) + delta_y, (dimension[1]/2) - delta_y + EPS, delta_y):
                for z in my_range(-(dimension[2]/2) + delta_z, (dimension[2]/2) - delta_z + EPS, delta_z):
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
        me.from_pydata(points, [], [])
        me.update()
        bpy.ops.object.editmode_toggle()


def my_range(start, stop, step):
            r = start
            while r < stop:
                yield r
                r += step


################# ROZTRASENIE #################


### roztrasenie bodov
def discrepancy(main_object_dimension, discrepancyX, discrepancyY, discrepancyZ,tempZ, axis):
    ob = bpy.data.objects['temp_grid']
    ob1 = bpy.data.objects['FractureMash_duplicate']
    mesh=bmesh.from_edit_mesh(bpy.context.object.data)

    if tempZ:
        temp_z = (main_object_dimension[2]/2 - main_object_dimension[2] / (axis[2] + 1))*2

    else:
        temp_z = 0
    for v in mesh.verts:


            v.co = (random_co(v.co[0],main_object_dimension[0]/(axis[0]+1),discrepancyX),random_co(v.co[1],main_object_dimension[1]/(axis[1] + 1),discrepancyY),random_co(v.co[2] + temp_z,main_object_dimension[2]/(axis[2] +1),discrepancyZ))

            ######## EXPERIMENT IS INSIDE ###############
            # if not is_inside(v.co,1.84467e+19,ob1):
            #     v.select = True
            #     bpy.ops.mesh.delete(type='VERT')

            if tempZ:
                temp_z -= (main_object_dimension[2]/(axis[2] +1))*2


    final_co_array = [ob.matrix_world * vert.co for vert in mesh.verts]
    bpy.context.scene.objects.active = bpy.context.scene.objects.active
    bpy.ops.object.mode_set(mode='OBJECT')

    return final_co_array


def random_co(coordinate, dimenzion,discrepancy):
    return  coordinate + random.uniform(-dimenzion*discrepancy,dimenzion*discrepancy)


def random_angle(angle,dicrepancy):
    return math.pi/180 * ( angle + random.uniform(-dicrepancy,dicrepancy))


###### TEST IF vervetx in mesh ###################################################

#
# def is_inside(p, max_dist, obj):
#     # max_dist = 1.84467e+19
#     point, normal, face = obj.closest_point_on_mesh(p, max_dist)
#     p2 = point-p
#     v = p2.dot(normal)
#     return not(v < 0.0)
####################### TVORBA ROVIN ############################


def make_planes(array_co,dimension,obj,x, y,z,axis,jitter):

    temp_array_x = []
    temp_array_y = []
    temp_array_z = []
    for v in array_co:
        if axis[0]:
            if (jitter[0] == 0 ) and (v[1] in temp_array_x) and ( x == 0):
                pass
            else:
                define_plane(dimension, v)
                bpy.ops.transform.rotate(value=random_angle(90, x), axis=(1, 0, 0))
                solidify()
                make_difference(obj)
                if v[1] not in temp_array_x:
                    temp_array_x.append(v[1])
        if axis[1]:
            if (jitter[1] == 0)  and (v[0] in temp_array_y )and (y==0):
                pass
            else:
                define_plane(dimension,v)
                bpy.ops.transform.rotate(value=random_angle(90, y), axis=(0, 1, 0))
                solidify()
                make_difference(obj)
                if v[0] not in temp_array_y:
                    temp_array_y.append(v[0])
        if axis[2]:
            if jitter[2] == 0 and  v[2] in temp_array_z and z==0:
                pass
            else:
                define_plane(dimension, v)
                bpy.ops.transform.rotate(value=random_angle(0, z), axis=(1, 0, 0))
                solidify()
                make_difference(obj)
                if v[2] not in temp_array_z:
                    temp_array_z.append(v[2])



def define_plane(dimension,v):
    bpy.ops.mesh.primitive_plane_add(location=(v[0], v[1], v[2]))
    plane = bpy.context.active_object
    plane.name = "FractureOnePartMesh"
    plane.dimensions = (dimension[0] * 3, dimension[1] * 3, 0)


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
    if (2, 78, 0) <= bpy.app.version:
        bpy.context.object.modifiers["{name}".format(name=c_name)].solver = 'CARVE'
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
    if (2, 78, 0) <= bpy.app.version:
        bpy.context.object.modifiers["{name}".format(name=c_name)].solver = 'CARVE'
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Boolean')
    bpy.data.objects[name].select = True
    obj.select = False
    bpy.ops.object.delete()


def solidify():
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].thickness = 0.0001
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Solidify')


################################## ROZDELENIE OBJEKTOV ###############################


## rozdelenie na male casti
def separate_loose(ob):
    bpy.data.objects[ob.name].select = True
    bpy.ops.mesh.separate(type="LOOSE")


#vytvara diery do objektu
def differ(obj,pos,dime,count,i):
    temp_dimensions = [None,None,None]
    bpy.ops.mesh.primitive_cube_add(location=(pos[0],pos[1],pos[2]))
    dif = bpy.context.active_object
    dif.name = "differ"
    dif.dimensions = (dime[0]-((dime[0]/count)*(2*i)-0.05),dime[1]-((dime[1]/count)*(2*i)-0.05),dime[2]-((dime[2]/count)*(2*i)-0.05))
    bpy.context.scene.update()
    temp_dimensions[0] = bpy.data.objects['differ'].dimensions[0] - 0.05
    temp_dimensions[1] = bpy.data.objects['differ'].dimensions[1] - 0.05
    temp_dimensions[2] = bpy.data.objects['differ'].dimensions[2] - 0.05
    bpy.ops.object.select_all(action='DESELECT')
    dif.select = True
    make_difference(obj,dif.name)
    position = dif.location
    return [position,temp_dimensions]


#prienik a rozdelenie objektu
def intersection_separate(copy_object,dimensions,rotation):
    make_intersection(copy_object,rotation)
    copy_object.dimensions = (dimensions[0] - 2, dimensions[1] - 2, dimensions[2] - 2)
    separate_loose(copy_object)


def delete_default_object(default_object):
    bpy.ops.object.select_all(action='DESELECT')
    default_object.select = True
    bpy.ops.object.delete()


###################### BLENDER MODUL FUNKCIE ###############################


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
