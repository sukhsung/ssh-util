import numpy as np
from bokeh.plotting import figure, show
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Slider, RangeSlider, CustomJS, LinearColorMapper
import bokeh.palettes

def enable_notebook():
    from bokeh.io import output_notebook
    output_notebook()
    
def imageBC( im ):
    # Force numpy array
    im = np.asarray( im )
    shape = im.shape
    if len(shape) == 3:
        print("Looks like stack, try imageBC")
        return
    elif len(shape) == 2:
        ny = shape[0]
        nx = shape[1]

    clim = [np.min(im), np.max(im)]

    # Place Holder (Required for Contrast)
    im_blank = np.zeros( (ny,nx) )
    
    p = figure(width=400, height=400,
            tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im")])
    p.x_range.range_padding = p.y_range.range_padding = 0
    p.grid.grid_line_width = 0

    # Initialize Colormap
    gray = bokeh.palettes.Greys256
    cmap = LinearColorMapper(palette=gray)
    
    #initialize a column datasource and assign first image into it
    src = ColumnDataSource(data={'im':[im]})
    
    #create the image render
    im_rend = p.image(image='im', x=0, y=0, dw=nx, dh=ny, level="image", color_mapper=cmap, source=src)


    #a widget to put a callback on
    sl_c = RangeSlider(start=clim[0], end=clim[1], value=(clim[0],clim[1]), step=(clim[1]-clim[0])/1000, title="Contrast")
    args = dict(src=src,im=im, im_blank=im_blank, sl_c=sl_c)
    code_c = """
            const clim = sl_c.value
            var image = im
            var image_c = im_blank

            for (let i=0; i<image.length; i++) {
                var cur_val = image[i]
                if ( cur_val > clim[1] ){
                    image_c[i] = clim[1]
                } else if ( cur_val < clim[0] ){
                    image_c[i] = clim[0]
                } else {
                    image_c[i] = image[i]
                }
            }
            
            src.data['im'] = [image_c]
            src.change.emit()
            """
    
    cb_c = CustomJS(args=args,code=code_c)
    
    sl_c.js_on_change('value',cb_c)
    lo = layout([p, sl_c])
    show(lo)

def sliceZ( im_stack ):
    # Force numpy array
    im_stack = np.asarray( im_stack )
    shape = im_stack.shape
    if len(shape) == 2:
        imageBC(im_stack)
        return
    elif len(shape) == 3:
        nz = shape[0]
        ny = shape[1]
        nx = shape[2]

    # 3D array -> List of 2D NP arrays
    im_stack_src = []
    for i in range(nz):
        im_stack_src.append( im_stack[i] )
    clim = [np.min(im_stack), np.max(im_stack)]

    # Place Holder (Required for Contrast)
    im_blank = np.zeros( (ny,nx) )
    
    p = figure(width=400, height=400,
            tooltips=[("x", "$x"), ("y", "$y"), ("value", "@im")])
    p.x_range.range_padding = p.y_range.range_padding = 0
    p.grid.grid_line_width = 0
    
    #initialize a column datasource and assign first image into it
    src = ColumnDataSource(data={'im':[im_stack[0]]})
    
    #create the image render
    gray = bokeh.palettes.Greys256
    cmap = LinearColorMapper(palette=gray)
    im_rend = p.image(image='im', x=0, y=0, dw=nx, dh=ny, level="image", color_mapper=cmap, source=src)


    #a widget to put a callback on
    sl_z = Slider(start=0,end=nz-1,value=0,step=1,width=100,title="Slice")
    sl_c = RangeSlider(start=clim[0], end=clim[1], value=(clim[0],clim[1]), step=(clim[1]-clim[0])/1000, title="Contrast")
    code_c = """
            const z = sl_z.value
            const clim = sl_c.value
            var image = im_stack[z]
            var image_c = im_blank

            for (let i=0; i<image.length; i++) {
                var cur_val = image[i]
                if ( cur_val > clim[1] ){
                    image_c[i] = clim[1]
                } else if ( cur_val < clim[0] ){
                    image_c[i] = clim[0]
                } else {
                    image_c[i] = image[i]
                }
            }
            
            src.data['im'] = [image_c]
            src.change.emit()
            """
    args = dict(src=src,
                im_stack=im_stack_src, 
                im_blank=im_blank, 
                sl_z=sl_z, 
                sl_c=sl_c)
    cb_c = CustomJS(args=args,code=code_c)

    
    sl_z.js_on_change('value',cb_c)
    sl_c.js_on_change('value',cb_c)
    lo = layout([p,sl_z, sl_c])
    show(lo)