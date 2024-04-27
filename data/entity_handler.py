from data.object_handler import *
from data.spell_handler import SpellHandler, Spell
from data.pathing_handler import PathingHandler
import pygame as pg
import glm
import random
from data.config import config
from data.structure_handler import structures
from data.deck_handler import DeckHandler
import cudart

class EntityHandler():
    
    def __init__(self, object_handler : ObjectHandler, cam):
        
        self.object_handler = object_handler
        self.spell_handler = SpellHandler(object_handler)
        self.pathing_handler = PathingHandler()
        self.entities = []
        self.on_init(cam)
        
    def on_init(self, cam) -> None:
        
        # creates player 
        player = Player(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', vao='diceguy', material='diceguy', obj_type='metal_box', scale=(.25, .25, .25), hitbox_type='largecube', hitbox_file_name='diceguy/diceguy')), cam, 100)
        self.entities.append(player)
        
    def get_ragdoll_objects(self):
        
        return list(filter(lambda n: n.ragdoll, self.entities))
    
    def update(self, delta_time):
        
        # updates spells
        self.spell_handler.update(delta_time)
        
        # updates entities
        for entity in self.entities: 
            
            # to change from ragdoll to stable
            if entity.ragdoll:
                if glm.length(entity.obj.hitbox.vel) < 4 and entity.obj.hitbox.rot_vel < np.pi and entity.obj.last_collided is not None: 
                    if type(entity) is Player and entity.ragdoll_distance > 1.5: 
                        self.entities[0].deck_handler.undiscard(self.entities[0].get_upward_side())
                    entity.ragdoll = False
                    entity.ragdoll_distance = 0
            
            # to change from stable to ragdoll
            else:
                if (glm.length(entity.obj.hitbox.vel) > 2 or entity.obj.hitbox.rot_vel > np.pi / 2) and entity.obj.last_collided is not None: entity.ragdoll = True
            
            # ragdoll
            if entity.ragdoll: 
                entity.ragdoll_distance += delta_time * abs(entity.obj.hitbox.rot_vel)
            else: 
                # sets velocities to zero
                for i in (0, 2): entity.obj.hitbox.vel[i] = 0
                entity.obj.hitbox.rot_vel = 0
            
            # moves entity based on AI, controls, etc
            entity.move(delta_time)
            
    def clear_all(self):
        
        while len(self.entities) > 1:
            self.entities[-1].remove_self()
        
    def set_player_camera(self, camera):
        self.entities[0].set_camera(camera)
        
    def get_entities_in_radius(self, pos, radius):
        
        in_range = {}
        for entity in self.entities:
            direction = entity.obj.pos - pos
            if glm.length(direction) <= radius: in_range[entity] = glm.normalize(direction)
        return in_range
    
    def get_random_jump_caster(self, obj, power, ragdoll = False, element = None, pathing = 'direct_distanced'):
        # gets spell caster based off of stats
        if element is None: element = self.spell_handler.element_handler.get_random_element()
        health, speed, casting_time = self.get_spellcaster_stats(power)   
        spell = self.spell_handler.create_spell(power, element)
        return JumpCaster(self, obj, health, speed, ragdoll, pathing, spells = [spell], power = power, max_cooldown = casting_time)
    
    def get_spellcaster_stats(self, power):
        # distributes power points to attribs
        left, health, speed, casting_time = power, 1, 1, 5
        while left > 0:
            option = random.randint(0, 100)
            if option < 90: health += 1
            elif option < 95 and casting_time > 1: 
                casting_time /= 2
                left /= 2
            else: speed += 1
            left -= 1
            
        return health, speed, casting_time
    
    def spawn_enemies_in_dungeon(self, power):
        
        # pulls data from structure files
        room_prints = structures
        rooms = self.object_handler.scene.chunk_handler.dungeon_handler.room_spawns
        
        # loops through rooms
        for room_pos, room in rooms.items():
            # gets room template from structure handler
            room_print = room_prints[room.file_name]
            for spawn_zone in room_print['entities']:
                # rolls random spawn chance
                if random.uniform(0.0, 1.0) > spawn_zone[2]: continue
                
                # offsets spawnzone by chunk and randomizes in radius
                pos = [room_pos[i] * 10 + 10 + spawn_zone[0][i] for i in range(3)] # random.uniform(-spawn_zone[2], spawn_zone[2]) * [1, 0, 1][i] 
                
                # now spawn something
                obj = Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=pos, scale=(.5, .5, .5))
                sc = self.get_random_jump_caster(obj, power)
                self.entities.append(sc)
            
            # for boss and spawn rooms
            if 'room-boss' in room.file_name:
                estring = room.file_name.split('-')[-1]
                element = self.spell_handler.element_handler.elements[estring]
                
                # adds boss enemy
                pos = [room_pos[i] * 10 + [23, 12, 23][i] for i in range(3)]
                obj = Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=pos, scale=(1.5, 1.5, 1.5), element = estring)
                health, speed, casting_time = self.get_spellcaster_stats(power * 5)
                boss = Boss(self, self.object_handler.add_object(obj), health=health, speed=speed, pathing='direct_distanced', power=power, spells=[], ragdoll=False, max_cooldown = casting_time, element=element)
                # creates new death function
                self.entities.append(boss)
                
                # adds tp zone in boss room
                self.object_handler.scene.load_zone_handler.add_inactive('exit', [pos[i] + [0, -3, 0][i] for i in range(3)], (4, 4, 4), 'dungeon' , (0, 1, 1), 5)
                
            if room.file_name == 'room-spawn':
                pos = [room_pos[i] * 10 + 13 for i in range(3)]
                self.entities[0].obj.set_pos(pos)
                self.entities[0].spawn_point = pos
    
    def build_spawn(self):
        self.entities[0].spawn_point = [50, 7, 20]
        self.entities[0].obj.set_pos([50, 7, 20])
        # shop guy
        self.entities.append(Entity(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', vao='diceguy', material='diceguy', obj_type='metal_box', scale=(.25, .25, .25), pos = (53, 7, 55), rot = (0, 0, 0), hitbox_type='largecube', hitbox_file_name='diceguy/diceguy', element = 'dark')), 1e9, 0, False))
        self.entities[-1].obj.set_rot((0, glm.radians(180), 0))

    def get_boss_health_info(self):
        
        for entity in self.entities:
            if type(entity) is not Boss: continue
            return entity.health, entity.max_health
        return 0, 0

class Entity():
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health, speed = 1, ragdoll = False):
        
        self.entity_handler = entity_handler
        self.ragdoll = ragdoll
        self.obj = obj
        self.max_health = health
        self.health = health
        self.speed = speed
        self.ragdoll_distance = 0
        self.spawn_point = [i for i in self.obj.pos]
        
    def move(self, delta_time):
        
        if self.obj.pos[1] < -20:
            self.obj.set_pos(self.spawn_point)
            self.obj.hitbox.set_vel((0, 0, 0))
    
    def take_hit(self, spell : Spell, origin):
        
        # spell effects
        self.health -= spell.damage
        
        # force
        direction = glm.normalize(self.obj.pos - origin)
        self.obj.hitbox.set_vel(direction * spell.force ** 2)
        
        # after checks
        if self.health <= 0:
            self.on_death()
        
    def on_death(self):
        
        self.entity_handler.entities[0].money += random.randint(1, self.max_health)
        self.entity_handler.object_handler.scene.ui_handler.update_texture = 2
        self.remove_self()
        
    def remove_self(self):
        
        # removes from handler lists
        self.entity_handler.entities.remove(self)
        self.entity_handler.object_handler.objects.remove(self.obj)
        
        # delete just in case
        del self.obj
        del self
        
    # def ray_cast_vec(self, origin, vec, tests = 100, multiplier = 1, starting_test = 0):
    def can_see(self, target):
        
        obj_pos = [self.obj.pos[i] + [0, 0.5, 0][i] for i in range(3)]
        target_pos = [target.pos[i] + [0, 0.5, 0][i] for i in range(3)]
        direction = (glm.vec3(target_pos) - obj_pos) / 100
        # detects if target is in line of sight
        return self.entity_handler.object_handler.scene.chunk_handler.ray_cast_vec(obj_pos, direction, starting_test = 5) is None
    
    # default to aiming at player
    def get_aiming_at(self):
        
        if self.can_see(self.entity_handler.entities[0].obj): return self.entity_handler.entities[0].obj.pos
        else: glm.vec3(0, 0 ,0) # fix
        
class Player(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, cam, health, speed = 5, ragdoll = False):
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        self.cam = cam
        self.deck_handler = DeckHandler(self)
        self.money = 0
        
    def after_init(self):
        
        # gives the player starting spells
        for _ in range(10): self.deck_handler.add_spell(self.entity_handler.spell_handler.create_spell(30))
        self.deck_handler.refill_hand()
        self.entity_handler.object_handler.scene.ui_handler.selected_inv_card = self.deck_handler.deck[0]
        
    def use_card(self, index):
        
        if not 0 <= index < len(self.deck_handler.hand): return
        self.entity_handler.object_handler.scene.sound_handler.play_sound('shoot')
        self.deck_handler.hand[index].get_bullets(self.obj.pos + self.cam.forward, np.array([i for i in glm.normalize(self.cam.looking_at())]), self.obj)
        self.deck_handler.discard_from_hand(index)
        self.deck_handler.refill_hand()
        
    def move(self, delta_time):
        
        super().move(delta_time)
        
        keys = pg.key.get_pressed()
        if keys[config['controls']['up']] and self.obj.last_collided is not None and self.ragdoll is False:
            
            # launches player with rotation
            direction = glm.normalize(glm.vec3(np.cos(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch)), 0, np.sin(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch))))
            direction += [0, 1, 0]
            self.obj.hitbox.rot_axis = glm.normalize(glm.cross(direction, (0, 1, 0)))
            self.obj.hitbox.vel = direction * 7
            self.obj.hitbox.rot_vel = np.pi
            self.ragdoll = True
        
        if self.ragdoll: return
        
        velocity = self.speed * delta_time
        key_pressed = False
        if keys[config['controls']['forward']]:
            self.obj.pos += glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[config['controls']['backward']]:
            self.obj.pos -= glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[config['controls']['left']]:
            self.obj.pos -= self.cam.right * velocity
            key_pressed = True
        if keys[config['controls']['right']]:
            self.obj.pos += self.cam.right * velocity
            key_pressed = True
            
        if key_pressed:
            self.obj.set_rot([0, -glm.radians(self.cam.yaw - 90), 0])
            
    def set_camera(self, camera):
        self.cam = camera
        
    # override function
    def on_death(self):
        
        self.entity_handler.object_handler.scene.enter_hub()
        
    def reset_player(self) -> None:
        
        # resets cards
        self.deck_handler.undiscard(1e6)
        self.health = self.max_health
        
    def get_upward_side(self) -> int:
        
        self.obj.hitbox.update_vertices()
        # encoded side directions NEEDS TO BE CHANGED
        sides = {
            6 : (self.obj.hitbox.get_face_normal(0), self.obj.hitbox.get_face_normal(1)),
            5 : (self.obj.hitbox.get_face_normal(2), self.obj.hitbox.get_face_normal(3)),
            1 : (self.obj.hitbox.get_face_normal(4), self.obj.hitbox.get_face_normal(5)),
            2 : (self.obj.hitbox.get_face_normal(6), self.obj.hitbox.get_face_normal(7)),
            3 : (self.obj.hitbox.get_face_normal(8), self.obj.hitbox.get_face_normal(9)),
            4 : (self.obj.hitbox.get_face_normal(10), self.obj.hitbox.get_face_normal(11))
            }
        
        # finds most similar vector to rot point
        point = (0, 1, 0)
        best, score = None, -1e6
        for num, dir in sides.items():
            if (dot := np.dot(point, dir[0])) > score or (dot := np.dot(point, dir[1])) > score: best, score = num, dot
        return best

    def is_in_boss_room(self):
        return self.entity_handler.object_handler.scene.chunk_handler.dungeon_handler.point_in_boss_room(self.obj.pos)


class Enemy(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing_type = 'direct'):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        match pathing_type:
            case 'direct': self.pathing = self.entity_handler.pathing_handler.get_direct(speed)
            case 'direct_distanced': self.pathing = self.entity_handler.pathing_handler.get_direct_distanced(speed, 7)
            case 'away': self.pathing = self.entity_handler.pathing_handler.get_away(speed)
            case _: assert False, 'pathing type not recognized'
        self.knows_player_location = False
        self.max_forget_time = 10
        self.forget_time = self.max_forget_time
        
    def move(self, delta_time): 
        
        super().move(delta_time)
        
        # do nothing if in ragdoll
        if self.ragdoll: return
        #self.obj.set_pos(self.pathing(self.obj.pos, self.entity_handler.entities[0].obj.pos, delta_time))
        
        player_pos = self.entity_handler.entities[0].obj.pos
        
        can_see_player = self.can_see(self.entity_handler.entities[0].obj)
        if can_see_player:
            self.knows_player_location = True
            self.forget_time = self.max_forget_time
            if (x := player_pos[0] - self.obj.pos[0]) == 0: x = 0.001
            angle = glm.atan((player_pos[2] - self.obj.pos[2]) / (x)) 
            if x < 0 : angle -= 3.1415
            #if (player_pos[2] - self.obj.pos[2]) < 0 and x < 0: angle += 3.1415
            self.obj.set_rot([0, -angle + glm.radians(90), 0])
        
        if self.knows_player_location:
            self.obj.set_pos(self.pathing(self.obj.pos, player_pos, delta_time))
            if not can_see_player: self.forget_time -= delta_time
            if self.forget_time <= 0: self.knows_player_location = False
        
class SpellCaster(Enemy):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing = 'direct_distanced', power = 0, spells : list = [], max_cooldown = 3):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll, pathing)
        self.max_cooldown = max_cooldown
        self.cooldown = max_cooldown
        self.spells = spells
        self.on_init(power)
        
    def on_init(self, power):
        if len(self.spells) == 0: self.spells.append(self.entity_handler.spell_handler.create_spell(power))
        match self.spells[0].launch_type:
            case 'confused':
                self.obj = self.entity_handler.object_handler.add_object(Object(self.entity_handler.object_handler, self.entity_handler.object_handler.scene, model.BaseModel, program_name='default', vao='d4', material='d4', obj_type='metal_box', scale=(1, 1, 1), pos=self.obj.pos, hitbox_type='fitted', hitbox_file_name='d4/d4', element=self.spells[0].element.name))
            case 'straight':
                self.obj = self.entity_handler.object_handler.add_object(Object(self.entity_handler.object_handler, self.entity_handler.object_handler.scene, model.BaseModel, program_name='default', vao='d6', material='d6', obj_type='metal_box', scale=(0.5, 0.5, 0.5), pos=self.obj.pos, hitbox_type='rectangle', hitbox_file_name='d6/d6', element=self.spells[0].element.name))
            case 'lob':
                self.obj = self.entity_handler.object_handler.add_object(Object(self.entity_handler.object_handler, self.entity_handler.object_handler.scene, model.BaseModel, program_name='default', vao='d20', material='d20', obj_type='metal_box', scale=(1, 1, 1), pos=self.obj.pos, hitbox_type='fitted', hitbox_file_name='d20/d20', element=self.spells[0].element.name))
            case _: assert False, 'uh oh, launch type no exist'
        
    def move(self, delta_time):
        
        # reduces spell cooldown time
        self.cooldown -= delta_time
        
        super().move(delta_time)
        
        # spell casting
        if self.cooldown < 0:
            if self.can_see(self.entity_handler.entities[0].obj):
                # has shot spell
                direction = glm.normalize(self.entity_handler.entities[0].obj.pos - self.obj.pos)
                random.choice(self.spells).get_bullets(self.obj.pos + direction * 2, np.array([i for i in direction]), self)
                self.cooldown = self.max_cooldown
                self.entity_handler.object_handler.scene.sound_handler.play_sound('shoot')
            else: self.cooldown += 0.5
            
class JumpCaster(SpellCaster):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing = 'direct', power = 0, spells : list = [], max_cooldown = 3, jump_strength = 7, max_jump_time = 7):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll, pathing, power, spells, max_cooldown)
        self.jump_strength = jump_strength
        self.max_jump_time = max_jump_time
        self.jump_time = max_jump_time
        
    def move(self, delta_time):
        
        super().move(delta_time)
        
        # enemy jumps
        self.jump_time -= delta_time
        if self.jump_time < 0:
            if self.can_see(self.entity_handler.entities[0].obj):
                self.jump_time = self.max_jump_time
                
                # gets direction to player
                direction = self.entity_handler.entities[0].obj.pos - self.obj.pos
                direction = glm.normalize((direction[0], 0, direction[2])) + [0, 1, 0]
                
                self.obj.hitbox.rot_axis = glm.normalize(glm.cross(direction, (0, 1, 0)))
                self.obj.hitbox.vel = direction * self.jump_strength
                self.obj.hitbox.rot_vel = np.pi
                self.ragdoll = True
            else: self.jump_time += 0.5
            
class Boss(JumpCaster):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing = 'direct', power = 0, spells : list = [], max_cooldown = 3, jump_strength = 7, max_jump_time = 7, element = None):
        
        if element is None: element = self.entity_handler.spell_handler.element_handler.get_random_element()
        self.element = element
        self.power = power
        super().__init__(entity_handler, obj, health, speed, ragdoll, pathing, power, spells, max_cooldown, jump_strength, max_jump_time)
        
        
    def on_death(self):
        
        self.entity_handler.object_handler.scene.load_zone_handler.move_to_active('exit')
        card = self.entity_handler.spell_handler.create_spell(self.power + 10)
        self.entity_handler.entities[0].deck_handler.add_spell(card)
        
        self.entity_handler.object_handler.scene.ui_handler.latest_card = card
        self.entity_handler.object_handler.scene.ui_handler.show_new_card = 5
        config['runtime']['simulate'] = False

        super().on_death()
        
    def on_init(self, power):
        for _ in range(3): self.spells.append(self.entity_handler.spell_handler.create_spell(power, self.element))
