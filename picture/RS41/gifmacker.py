import imageio 
import pathlib

def compose_gif(): 
    g = pathlib.Path('.').glob('*.png')
    gif_images = [] 
    for path in list(g): 
        print(path, flush=True)
        gif_images.append(imageio.imread(path)) 
        imageio.mimsave("RS41.gif",gif_images,fps=1)


compose_gif()