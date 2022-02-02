from ursina import *


class RubiksCube(Ursina):
    ROTATION_DICTIONARY = {'U': ['y', 1, 90, False], 'D': ['y', -1, -90, False],
                           'L': ['x', -1, -90, False], 'R': ['x', 1, 90, False],
                           'F': ['z', -1, 90, False], 'B': ['z', 1, -90, False],
                           'x': ['x', 2, 90, True], 'y': ['y', 2, 90, True],
                           'z': ['z', 2, 90, True]}

    ROTATION_SPEED = 0.6

    def __init__(self, solution='', start_position=''):
        super().__init__()
        self.set_up_window()
        self.set_up_camera()
        self.cube = []
        self.action_trigger = True
        self.center = Entity()
        self.str_solution = solution
        self.solution = solution.split()
        self.scramble = self.solution + self.set_up_start_position(start_position)
        self.solution_text = Text(text=solution, origin=(0,12), color=color.white)
        self.create_cube()
        self.shuffle()

    @staticmethod
    def set_up_window():
        window.borderless = False
        window.size = (800, 800)
        window.color = color.black10
        # window.position = (200, 200)

    @staticmethod
    def set_up_camera():
        camera.position = (5.7, 6.5, -10)
        camera.rotation_x = 30
        camera.rotation_y = -30

    @staticmethod
    def parse_key(key):
        print(key)
        new_key = key
        for cn in ("'", "2"):
            new_key = new_key.replace(cn, '')
        return new_key

    @staticmethod
    def set_angle_n_speed(key, angle, time_rot_coeff=0):
        if "'" not in key:
            angle = -angle
        if '2' in key:
            angle *= 2
            time_rot_coeff *= 2

        return angle, time_rot_coeff

    @staticmethod
    def set_up_start_position(start_position):
        start_position = start_position.split()
        for i in range(len(start_position)):
            print(i)
            if "'" in start_position[i]:
                start_position[i] = start_position[i].replace("'", '')
            else:
                start_position[i] = start_position[i] + "'"

        print('start_position', start_position[::-1])

        return start_position[::-1]

    def shuffle(self):
        while self.scramble:
            key = self.scramble.pop()
            new_key = self.parse_key(key)
            if new_key not in self.ROTATION_DICTIONARY:
                continue
            axis, shift, angle, is_all_cube = self.ROTATION_DICTIONARY[new_key]
            self.side_for_rotation(axis, shift, is_all_cube)
            angle, _ = self.set_angle_n_speed(key, angle)
            eval(f'self.center.animate_rotation_{axis}({angle}, duration = 0)')

    def animation_trigger(self):
        self.action_trigger = not self.action_trigger

    def rotate(self):
        if not (self.action_trigger and self.solution):
            return

        time_rot_coeff = 1
        key = self.solution.pop(0)
        new_key = self.parse_key(key)
        axis, shift, angle, is_all_cube = self.ROTATION_DICTIONARY[new_key]
        self.side_for_rotation(axis, shift, is_all_cube)
        angle, time_rot_coeff = self.set_angle_n_speed(key, angle, time_rot_coeff)
        eval(f'self.center.animate_rotation_{axis}({-angle}, duration = self.ROTATION_SPEED*time_rot_coeff)')
        self.action_trigger = False
        invoke(self.animation_trigger, delay=self.ROTATION_SPEED * time_rot_coeff + 0.11)
        self.solution_text.text = ' '.join(self.solution)

    def create_cube(self):
        texture_number = 1
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    self.cube.append(
                        Entity(model='model/cube.obj',
                               texture=f'textures/{texture_number}.png',
                               position=(x, y, z),
                               scale=0.5))
                    texture_number += 1

    def side_for_rotation(self, axis, shift, is_rotate_all=False):
        for c in self.cube:
            c.position, c.rotation = round(c.world_position, 1), c.world_rotation
            c.parent = scene

        self.center.rotation = 0

        for c in self.cube:
            if is_rotate_all:
                c.parent = self.center

            elif eval(f'c.position.{axis}') == shift:
                c.parent = self.center

    def input(self, key):
        if key == 'space':
            self.rotate()
