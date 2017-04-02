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
import sys

from bpy.types import Operator,Panel  
from bpy.props import IntProperty, BoolProperty,EnumProperty



class Create_fracture(Panel):
    bl_idname = "object.fracture"        
    bl_label = "Create Fracture" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Fracture"
    bl_options = {'DEFAULT_CLOSED'}
    bpy.types.Object.pieces = IntProperty(  
           name="subdivide",
           default=5,
           min=2,
           soft_max = 10)
    bpy.types.Object.type_p = EnumProperty(items= (('0', 'Cube', 'Cubes'),    
                                                 ('1', 'Block', 'Blocks'),    
                                                 ('2', 'Sphere', 'Spheres'),    
                                                 ('3', 'Self', 'Copies'),
                                                 ('4','Random','Random')),
                                                 name = "choose fracture type")
    bpy.types.Object.bomb = BoolProperty(name = "Explosive Ready")



    ## modul je aktivny len pri objekte typu mesh
    @classmethod
    def poll(cls, context):
        if (context.active_object is not None):
            return context.active_object.type == "MESH"
        else:
            return False

        
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
        row.operator(Make_Fracture.bl_idname)

class Make_Fracture(Operator):
    bl_label = "Create"
    bl_idname = "make.fract"
    
    def execute(self,context):
        default_object,copy_object =  copy_selected_object()
        #nastevenie mien Meshov      
        default_object.name = "FractureMash_Default"
        copy_object.name = "FractureMash_duplicate"
        #nastavenie vlastnosti
        position = properties(default_object)[0] 
        dimensions = properties(default_object)[1] 
        rotation = properties(default_object)[2]
        pieces = properties(default_object)[3] 
        copy_object.rotation_euler = (0,0,0)
        default_object.rotation_euler = (0,0,0)
        default_object.draw_bounds_type = "CAPSULE"

        if default_object.type_p == "4":
                create_temp_cube_random(position,dimensions,pieces)
                delete_mesh()
                array_co = disprepancy(dimensions)
                make_planes(array_co,dimensions,copy_object)

        elif default_object.bomb == True:
           explode(copy_object,position,dimensions,pieces,default_object.type_p)
        else:
            if default_object.type_p=="0":
                create_cubes(position,dimensions,pieces)      
            elif default_object.type_p=="1":
                create_fract(position,dimensions,pieces)
               
            elif default_object.type_p=="2":
                create_sphere(position,dimensions,pieces)
            
            elif default_object.type_p=="3":
                create_duply(position,dimensions,pieces)
            # intersection_separate(default_object,rotation)
            #### robi separaciu objektu zakomentovane pretoze rodim random

           
                
##                random_planes(pieces,position,dimensions,ob)
##            separate_loose(ob)
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
        return
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
    axis = 1
    create_count(pieces,dim,axis,fract,1.004,name,inner)

#vytvory malu kocku 
def create_cubes(pos,dim,pieces,name = "FractureOnePartMesh",inner = False):
    props = properties_object(dim,pieces)
    bpy.ops.mesh.primitive_cube_add(location=((pos[0]-dim[0]/2)+props[1],(pos[1]-dim[1]/2)+props[1],(pos[2]-dim[2]/2)+props[1]))
    object_name(props[0],pieces,dim,1.004,name,inner)
## grip pre random
def create_temp_cube_random(pos,dim,pieces,inner = False):
    props = properties_object(dim,pieces)
    bpy.ops.mesh.primitive_plane_add(location=((pos[0]-dim[0]/2)+props[1],(pos[1]-dim[1]/2)+props[1],pos[2]))
    object_name(props[0],pieces,dim,1,"temp_grip",inner)

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


#vytvory plany cez ktore sa interpoluje
def planes(rotate,pos,dim):
    side = random.choice([-1,1])
    rand0 = random.randint(0,(dim[0]//2))
    rand1 = random.randint(0,(dim[1]//2))
    rand2 = random.randint(0,(dim[2]//2))
    bpy.ops.mesh.primitive_plane_add(location=(pos[0]+rand0*side,pos[1]+rand1*side,pos[2]+rand2*side))
    plane = bpy.context.active_object
    plane.dimensions = (dim[0]*3,dim[1]*3,dim[2]*3)  
    bpy.ops.transform.rotate(value = rotate, axis=(random.randrange(0,6),random.randrange(0,6),random.randrange(0,6)))
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].thickness = 0.001
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Solidify')
    return plane


def random_planes(count,pos,dim,ob):
    for i in range(count*4):
        rotate = random.randint(1,180)
        p=planes(math.pi/180*rotate,pos,dim)
        plane_differ(p,ob)

    
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


## bevel modifikator 
def bevel(ob):
    bpy.context.scene.objects.active = ob 
    bpy.ops.object.modifier_add(type='BEVEL')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].width = 0.3
    bpy.ops.object.modifier_apply(apply_as='DATA',modifier='Bevel')

def solidify():
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    c_name = bpy.context.object.modifiers[0].name
    bpy.context.object.modifiers["{name}".format(name=c_name)].thickness = 0.001
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
    array = [Meshobject.location,Meshobject.dimensions,Meshobject.rotation_euler[:],Meshobject.pieces]
    return array

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
 
def delete_mesh():
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.delete(type="EDGE_FACE")


### roztrasenie bodov
def disprepancy(main_object_dimension):
    coordinate_array = []
    final_co_array = []

    ob = bpy.data.objects['temp_grip']
    dim = ob.dimensions
    ob.dimensions = (dim[0] * 0.7, dim[1] * 0.7, 0)
    mesh=bmesh.from_edit_mesh(bpy.context.object.data)
    for v in mesh.verts:
        if [v.co[0],v.co[1],v.co[2]] not in coordinate_array:
            coordinate_array.append([v.co[0],v.co[1],v.co[2]])
            v.co = (random_co(v.co[0],main_object_dimension[0]//2),random_co(v.co[1],main_object_dimension[1]//2),random_co(v.co[2],main_object_dimension[2]//2))
        else:

            v.select = True
    bpy.ops.mesh.delete(type="VERT")
    final_co_array = [ob.matrix_world * vert.co for vert in mesh.verts]

    # trigger viewport update
    bpy.context.scene.objects.active = bpy.context.scene.objects.active
    bpy.ops.object.mode_set(mode='OBJECT')
    dim = bpy.context.object.dimensions
    bpy.context.object.dimensions = (dim[0]*0.99,dim[1]*0.99,dim[2]*0.99)
    return final_co_array

def random_co(coordinate, dimenzion):
    return coordinate + random.uniform(-dimenzion*(2/3),dimenzion*(2/3))


def random_angle(angle):
    return angle + random.uniform(-20,20)

def make_planes(array_co,dimension,obj):
    temp = None
    rotate1 = math.pi/180*random.randint(1,360)
    rotate2 = math.pi/180*random.randint(1,360)
    counter = 0
    temp_array =[]
    for v in array_co:
        for i in range(2):
            bpy.ops.mesh.primitive_plane_add(location=(v[0],v[1],v[2]))
            plane = bpy.context.active_object
            plane.name = "FractureOnePartMesh"
            plane.dimensions = (dimension[0]*3,dimension[1]*3,0)
            if i == 1:
                bpy.ops.transform.rotate(value = random_angle(rotate1), axis=(random.randrange(0,6),random.randrange(0,6),random.randrange(0,6)))
            else:
                bpy.ops.transform.rotate(value = random_angle(rotate2), axis=(random.randrange(0,6),random.randrange(0,6),random.randrange(0,6)))
            
            solidify()
            counter+=1
            make_difference(obj)



    # make_difference(obj)










# ##oznacenie vsetkych novo vytvorench objektov
def group():
    for ob in bpy.context.scene.objects:
        if "FractureOnePartMesh" in ob.name:
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
    bpy.ops.object.join()
    all = bpy.context.active_object
    all.name = "FractureOnePartMesh"
    bpy.ops.transform.resize(value=(1.01,1.01,1.01))
    

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
            print([pos_dim[1][0],math.ceil(pieces*(pos_dim[1][0]/minimal)) * (minimal/pieces)])
            print([pos_dim[1][1],math.ceil(pieces*(pos_dim[1][1]/minimal)) * (minimal/pieces)])
            print([pos_dim[1][2],math.ceil(pieces*(pos_dim[1][2]/minimal)) * (minimal/pieces)])
            if(pos_dim[1][0] < math.ceil(pieces*(pos_dim[1][0]/minimal)) * (minimal/pieces)
                or pos_dim[1][1] < math.ceil(pieces*(pos_dim[1][1]/minimal)) * (minimal/pieces)
               or pos_dim[1][2] < math.ceil(pieces*(pos_dim[1][2]/minimal)) * (minimal/pieces)):
                types(typ, pos_dim[0], pos_dim[1], ((count-inr)*(2**k)),"FractureOnePartMesh_" + str(i+1),True)
            else:
                types(typ, pos_dim[0], pos_dim[1], (count-inr)*(2**k),"FractureOnePartMesh_" + str(i+1))
            # raise Exception()
            ob = bpy.context.active_object
        inr+=2
        print((i,n))
        k+=1
    group()

   
def register():
    bpy.utils.register_class(Create_fracture)
    bpy.utils.register_class(Make_Fracture)
   

def unregister():
    bpy.utils.unregister_class(Create_fracture)
    bpy.utils.unregister_class(Make_Fracture)

    
if __name__ == "__main__":
    register()
