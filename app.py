from flask import Flask, jsonify, render_template
import os
import imageio
import numpy as np
import scipy.misc
import glob
from skimage.morphology import binary_erosion, binary_dilation

app = Flask(__name__, static_folder="web")

@app.route('/images')
def serve_images():
    return jsonify(os.listdir('data/images'))

@app.route('/threshold/<string:img>/<int:R_min>/<int:R_max>/<int:G_min>/<int:G_max>/<int:B_min>/<int:B_max>')
def threshold_image(img, R_min, R_max, G_min, G_max, B_min, B_max):
    # files = glob.glob('web/data/thresholded/*')
    # os.remove(files[0])
    delete_files('thresholded')
    morph_delete_files()
    img_arr = imageio.imread(f'data/images/{img}')
    R = img_arr[:, :, 0]
    G = img_arr[:, :, 1]
    B = img_arr[:, :, 2]

    mask = ((R>R_min) & (R<R_max) & (G>G_min) & (G<G_max) & (B>B_min) & (B<B_max))
    # imageio.imwrite("web/data/thresholded-mask.png", mask.astype(np.uint8)*255)
    imageio.imwrite(f"web/data/thresholded/{img.replace('.','-')}-{R_min}-{R_max}-{G_min}-{G_max}-{B_min}-{B_max}.png", mask.astype(np.uint8)*255)
    imageio.imwrite(f"web/data/morph/morph_init.png", mask.astype(np.uint8)*255)
    return ('', 204)

def delete_files(folder):
    files = glob.glob(f'web/data/{folder}/*')
    os.remove(files[0])

def morph_delete_files():
    files = glob.glob(f'web/data/morph/*')
    for f in files:
        os.remove(f)
    files = glob.glob(f'web/data/masked_morphimg/*')
    for f in files:
        os.remove(f)


@app.route('/apply_mask/<string:img>/<int:R_min>/<int:R_max>/<int:G_min>/<int:G_max>/<int:B_min>/<int:B_max>')
def apply_mask(img, R_min, R_max, G_min, G_max, B_min, B_max):
    delete_files('masked_img')
    files = glob.glob('web/data/thresholded/*')
    mask = imageio.imread(files[0])
    img_arr = imageio.imread(f'data/images/{img}')
    img_out = img_arr*(mask//255).reshape(*mask.shape, 1)
    imageio.imwrite(f"web/data/masked_img/{img.replace('.','-')}-{R_min}-{R_max}-{G_min}-{G_max}-{B_min}-{B_max}.png", img_out)
    return ('', 204)


# def remove_file(filename):
#     os.remove(filename)
# last_file = 'web/data/morph/morph_init.png'
operations = {'dilation':binary_dilation, 'erosion':binary_erosion}
@app.route('/morph/<string:process>/<string:img>/<int:radius>')
def morph(process, img, radius):
    op = operations[process]
    selem = np.zeros((50, 50))

    mask = imageio.imread(f'web/data/morph/morph_init.png')
    ci = 25
    cj = 25
    # Create index arrays to z
    I,J=np.meshgrid(np.arange(50),np.arange(50))

    # calculate distance of all points to centre
    dist=np.sqrt((I-ci)**2+(J-cj)**2)

    # Assign value of 1 to those points where dist<cr:
    selem[np.where(dist<=radius)]=1
    mask_new = op(mask, selem)
    imageio.imwrite(f"web/data/morph/morph_new_{img.replace('.','-')}-{radius}-{process}.png", mask_new.astype(np.uint8)*255)
    
    apply_morphed_mask(process, img, radius)
    return ('', 204)

# @app.route('/apply_mask/<string:process>/<string:img>/<int:radius>')
def apply_morphed_mask(process, img, radius):
    # delete_files('masked_img')
    mask = imageio.imread(f"web/data/morph/morph_new_{img.replace('.','-')}-{radius}-{process}.png")
    img_arr = imageio.imread(f'data/images/{img}')
    img_out = img_arr*(mask//255).reshape(*mask.shape, 1)
    imageio.imwrite(f"web/data/masked_morphimg/morph_masked_{img.replace('.','-')}-{radius}-{process}.png", img_out)
    return ('', 204)
# @app.route('/maskthres')