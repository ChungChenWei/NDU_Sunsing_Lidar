import imageio 
import pathlib

def compose_gif(): 
    g = pathlib.Path('.').glob('*.png')
    gif_images = [] 
    for path in list(g): 
        print(path, flush=True)
        gif_images.append(imageio.imread(path)) 
        imageio.mimsave("ST.gif",gif_images,fps=3)


compose_gif()