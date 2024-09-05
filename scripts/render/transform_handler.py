import moderngl as mgl
import numpy as np


class TransformHander:
    def __init__(self, scene) -> None:
        # Reference to the eviornment
        self.scene = scene
        self.ctx   = scene.ctx

        # Dicts to store the programs and transforms
        self.transforms = {}
        self.programs = {}

        # Load defaults
        self.load_transform('model_transform', 'model_transform', ['position'], '3f 3f 3f 3f', ('in_position', 'obj_position', 'obj_rotation', 'obj_scale'))

    def transform(self, transform_key, data):
        """
        Transforms the given data using the specified transform
        """
        
        return self.transforms[transform_key].transform(data)

    def load_transform(self, name: str, program_name: str, output: list, format: str, attribs: iter):
        """
        Loads a transformation shader. 
        Args:
            name: str
                Key that will be used in the dicts and transform() function to rtefernce the transform
            program_name: str
                Name of the shader file (without the extension) (Files should be in the 'shaders/transforms' folder)
            output: list
                The varyings of the transform program. These are the "out's" in the shader.
            format: str
                The format of the transform input attributes
            attribs: iter
                All input attributes needed to run the transformation
        """
        
        self.programs[name] = self.load_program(program_name, output)
        self.transforms[name] = Transform(self.ctx, self.programs[name], format, attribs)

    def load_program(self, name: str='default', output=[]) -> mgl.Program:
        """
        Creates a shader program from a file name.
        Parses through shaders to identify uniforms and save for writting
        """

        # Read the shader (No frag)
        with open(f'shaders/transforms/{name}.vert') as file:
            vertex_shader = file.read()

        # Create a program with shaders
        program = self.ctx.program(vertex_shader=vertex_shader, varyings=output,)
        return program


class Transform:
    def __init__(self, ctx, program, format, attribs, output_size=3, buffer_reserve=100000) -> None:
        """
        Container for all the data needed with a loaded transformation shader
        """
        
        self.ctx = ctx
        self.output_size = output_size
        self.input_buffer = ctx.buffer(reserve=buffer_reserve)
        self.vao = ctx.vertex_array(program, [(self.input_buffer, format, *attribs)])

    def transform(self, data):
        """
        Transforms the given data according to the current parameters
        """
        
        # Get the number of vertices
        N = len(data)

        # Write the input data to the vao buffer
        self.input_buffer.write(data)

        # Transform the data and read from buffer to np array
        output_data = self.ctx.buffer(np.zeros(shape=(N, self.output_size), dtype='f4'))
        output_data = self.ctx.buffer(reserve=(N * self.output_size * 4))
        self.vao.transform(output_data, vertices=N)
        output_data = np.frombuffer(output_data.read(), 'f4')

        return output_data