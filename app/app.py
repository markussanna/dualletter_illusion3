import cadquery as cq
import streamlit as st
import os
import sys
from pathlib import Path
import time
from stlcreation.heartfile import create_hollow_heart, create_text_object, create_heart_with_text
from streamlit_stl import stl_from_file

# Initialize session state
if 'text1' not in st.session_state:
    st.session_state.text1 = "STOP"
if 'text2' not in st.session_state:
    st.session_state.text2 = "WORK"
if 'rendering_method' not in st.session_state:
    st.session_state.rendering_method = "Regular"
if 'render_requested' not in st.session_state:
    st.session_state.render_requested = False
if 'rendering_complete' not in st.session_state:
    st.session_state.rendering_complete = False
if 'render_start_time' not in st.session_state:
    st.session_state.render_start_time = None

SPECIAL_CHARS = ['♥','♦','♣','♠','♪','♫','►','◄']

def get_fonts_path():
    """Get the absolute path to the resource, works for both development and PyInstaller bundle."""
    try:
        # PyInstaller stores files in a temporary folder _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Development mode
        base_path = Path(__file__).parent.parent

    return base_path / 'fonts'

def letter(let, angle, fontPath=""):
    """Extrude a letter, center it and rotate of the input angle"""
    wp = (cq.Workplane('XZ')
        .text(let, fontsize, extr, fontPath=fontPath, valign='bottom')
        )
    b_box = wp.combine().objects[0].BoundingBox()
    x_shift = -(b_box.xlen/2 + b_box.xmin )
    wp = (wp.translate([x_shift,extr/2,0])
        .rotate((0,0,0),(0,0,1),angle)
        )
    return wp

def dual_text(text1, text2, fontPath='', 
              save='stl', 
              b_h=2, b_pad=2, b_fil_per=0.8, space_per=0.3, 
              extrab_h=1, extrab_rad=2, extrab_mask='',
              export_name='file'):
    print(f"DEBUG: dual_text called with text1='{text1}', text2='{text2}'")
    """Generate the dual letter illusion from the two text and save it"""
    space = fontsize*space_per # spece between letter
    res = cq.Assembly() # start assembly
    last_ymax = 0
    for ind, ab in enumerate(zip(text1, text2)):
        try:
            a = letter(ab[0], 45, fontPath=fontPath)
            b = letter(ab[1], 135, fontPath=fontPath,)
            a_inter_b = a & b
            b_box = a_inter_b.objects[0].BoundingBox()
            translate_vect = [0, -b_box.ymin, 0]
            if ind:
                translate_vect[1] += last_ymax + space
            a_inter_b = a_inter_b.translate(translate_vect)
            last_ymax = a_inter_b.objects[0].BoundingBox().ymax
            res.add( a_inter_b) # add the intersection to the assebmly
            if extrab_mask and len(extrab_mask) > ind and extrab_mask[ind] != '_':
                res.add(cq.Workplane('XY')
                        .circle(extrab_rad//2)
                        .extrude(extrab_h)
                        .translate(translate_vect)
                        )
        except:
            last_ymax += space*1.5

    b_box = res.toCompound().BoundingBox() # calculate the bounding box
    # add the base to the assembly
    res.add(cq.Workplane()
            .box(b_box.xlen+b_pad*2, b_box.ylen+b_pad*2, b_h, centered=(1,0,0))
            .translate([0, -b_pad, -b_h])
            .edges('|Z')
            .fillet(b_box.xlen/2*b_fil_per)
            )
    # convert the assemly to a shape and center it
    res = res.toCompound()
    res = res.translate([0, -b_box.ylen/2,0])
    # export the files
    cq.exporters.export(res, f'file_display.stl')
    cq.exporters.export(res, f"{export_name}.{save}")

def heartLampRendering(text1, text2, fontPath='', 
                      save='stl', 
                      b_h=2, b_pad=2, b_fil_per=0.8, space_per=0.3, 
                      extrab_h=1, extrab_rad=2, extrab_mask='',
                      export_name='file'):
    print(f"DEBUG: heartLampRendering called with text1='{text1}', text2='{text2}'")
    """Generate a heart-shaped lamp with dual text illusion"""
    space = fontsize*space_per
  #  res = cq.Assembly()
    last_ymax = 0
    
    # Create heart-shaped base first
   # Create heart-shaped base first
    
    heart_with_text = create_heart_with_text(
    heart_height=500, 
    thickness=10, 
    height=15,
    text="Tanja", 
    font_size=100, 
    font_name="Brush Script",
    text_height=10,
    text_offset=0.1
    )
    # bb = heart_with_text.val().BoundingBox()
    # length = bb.xlen
    # width = bb.ylen
    # height = bb.zlen
    # print(f"Length (X): {length}, Width (Y): {width}, Height (Z): {height}")

    #show_object(heart_with_text, name="heart")

    
    # Export files
    cq.exporters.export(heart_with_text, f'file_display.stl')
    cq.exporters.export(heart_with_text, f"{export_name}.{save}")

# Callback function for render button
def on_render_click():
    print(f"DEBUG: Render button clicked, setting requested=True, complete=False")
    st.session_state.render_requested = True
    st.session_state.rendering_complete = False
    st.session_state.render_start_time = time.time()

if __name__ == "__main__":
    st.set_page_config(page_title="TextTango", page_icon="random", layout="wide", initial_sidebar_state="collapsed")
    for file in os.listdir():
        if 'file' in file:
            try:
                os.remove(file)
            except:
                print(f'Cannot remove file {file}')

    st.title('TextTango: Dual Letter Illusion')
    st.write("Generate a custom dual letter illusion, a 3d ambigram! If you like the project put a like on [Printables](https://www.printables.com/it/model/520333-texttango-dual-letter-illusion) or [support me with a coffee](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)! On Printables you can find more info about the project.", unsafe_allow_html=True)
    st.write("The Web App supports all [Google Fonts](https://fonts.google.com/), check them out!", unsafe_allow_html=True)

    st.markdown("""
### DISCLAIMER
#### Streamlit Cloud is a free platform, and has some limitations. The app often crashes and usually reboot after some hours. 
#### If you want to use the app without interruptions, leave a like on [Printables Page](https://www.printables.com/it/model/520333-texttango-dual-letter-illusion) and read the instructions and download the app from the [GitHub Release Page](https://github.com/Lucandia/dual_letter_illusion/releases).
""",    
    unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    # Input type
    with col1:
        text1 = st.text_input('First text', value=st.session_state.text1, key='text1_input')
        st.session_state.text1 = text1  # Update session state
        special_chars1 = st.columns(8)
        for i, char in enumerate(SPECIAL_CHARS):
            with special_chars1[i]:
                if st.button(char, key=f"btn1_{char}"):
                    st.session_state.text1 += char
                    st.rerun()
    with col2:
        text2 = st.text_input('Second text', value=st.session_state.text2, key='text2_input')
        st.session_state.text2 = text2  # Update session state
        special_chars2 = st.columns(8)
        for i, char in enumerate(SPECIAL_CHARS):
            with special_chars2[i]:
                if st.button(char, key=f"btn2_{char}"):
                    st.session_state.text2 += char
                    st.rerun()
    with col3:
        fontsize = st.number_input('Font size', min_value=1, max_value=None, value=20)
        extr = fontsize*2 # extrude letter

    if len(text1) != len(text2):
        st.warning("The two texts don't have the same length, letters in excess will be cut", icon="⚠️")
    if not text1.isupper() or not text2.isupper():
        st.warning("Non-capital letters with different height lead to bad results", icon="⚠️")

    col1, col2, col3 = st.columns(3)
    # Input type 
    font_dir = get_fonts_path()
    fonts = [f for f in os.listdir(font_dir) if '.' != f[0]]
    with col1:
        font_name = st.selectbox('Select font', ['lato'] + sorted(fonts))
    with col2:
        font_type_list = [f for f in os.listdir(font_dir / font_name) if '.ttf' in f and '-' in f]
        # font with explicit type (-bold, -regular, ...)
        if font_type_list:
            font_start_name = font_type_list[0].split('-')[0]
            font_type_list_name = [f.split('-')[1].strip('.ttf') for f in font_type_list]
            font_type = st.selectbox('Font type', sorted(font_type_list_name))
            font_type_pathname = font_start_name + '-' + font_type + '.ttf'
            font_path = font_dir / font_name / font_type_pathname
        else: # font without explicit type
            font_type_list = [f for f in os.listdir(font_dir / font_name) if '.ttf' in f]
            font_type = st.selectbox('Font type', sorted(font_type_list))
            font_path = font_dir / font_name / font_type
    with col3:
        space = st.slider('Letters space (%)', 0, 200, step=1, value=30) / 100
    # base parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        b_h = st.slider('Base height', 0.0, float(fontsize)/2, step=0.1, value=1.0)
    with col2:
        b_pad = st.slider('Base Padding', 0.0, float(fontsize)/2, step=0.1, value=2.0)
    with col3:
        b_fil_per = st.slider('Base fillet (%)', 0, 100, step=1, value=80) / 100

    # add base mask
    extra_mask = ''
    extrab_h = 0
    extrab_rad = 0
    if st.toggle('Add extra base for letters', value=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            default_mask = ''.join(['_' if i > 0 else 'X' for i in range(len(text1))])
            extra_mask = st.text_input('Text mask', value=default_mask,
                                       help="The underscore '_' means no extra base is added, the 'X' means an extra base is added at the corresponding letter position")
            if len(extra_mask) != len(text1):
                st.warning("The mask must have the same length as the text", icon="⚠️")
        with col2:
            extrab_h = st.slider('Height', 0.0, float(fontsize), step=0.1, value=1.0)
        with col3:
            extrab_rad = st.slider('Radius', 0.0, float(fontsize), step=0.1, value=2.0)

    col1, _, _ = st.columns(3)
    with col1:
        out = st.selectbox('Output file type', ['stl', 'step'])
            
    rendering_method = st.radio(
        "Rendering Method:",
        ["Regular", "Heart Lamp"],
        index=0 if st.session_state.rendering_method == "Regular" else 1,
        horizontal=True,
        help="Choose between standard rendering or heart-shaped lamp design",
        key="rendering_method_radio"
    )
    
    # Update session state when selection changes
    if rendering_method != st.session_state.rendering_method:
        print(f"DEBUG: Rendering method changed from {st.session_state.rendering_method} to {rendering_method}")
        st.session_state.rendering_method = rendering_method
     # ADD DEBUG PRINT RIGHT HERE:
    print(f"DEBUG: Current state - requested={st.session_state.render_requested}, complete={st.session_state.rendering_complete}, method={st.session_state.rendering_method}")    
    # Render button with callback
    if st.button('Render', on_click=on_render_click):
        pass  # The callback handles the action
        
    # Only render if the button was clicked and rendering is not complete
    if st.session_state.render_requested and not st.session_state.rendering_complete:
        print(f"DEBUG: Starting render, method={st.session_state.rendering_method}, requested={st.session_state.render_requested}, complete={st.session_state.rendering_complete}")
        with st.spinner('Wait for it...'):
            # Use the session state value
            if st.session_state.rendering_method == "Regular":
                print("DEBUG: Calling dual_text")
                dual_text(text1, text2, fontPath=str(font_path), save=out, 
                          b_h=b_h, b_pad=b_pad, b_fil_per=b_fil_per, space_per=space,
                          extrab_h=extrab_h, extrab_rad=extrab_rad, extrab_mask=extra_mask)
            else:  # Heart Lamp method
                print("DEBUG: Calling heartLampRendering")
                heartLampRendering(text1, text2, fontPath=str(font_path), save=out, 
                                  b_h=b_h, b_pad=b_pad, b_fil_per=b_fil_per, space_per=space,
                                  extrab_h=extrab_h, extrab_rad=extrab_rad, extrab_mask=extra_mask)
        
        # Mark rendering as complete
        st.session_state.rendering_complete = True
        st.session_state.render_requested = False
        print(f"DEBUG: Render complete, setting requested=False, complete=True")
        # Calculate rendering time
        end_time = time.time()
        render_time = int(end_time - st.session_state.render_start_time)
        
        # Show results
        if f'file.{out}' not in os.listdir():
            st.error('The program was not able to generate the mesh.', icon="🚨")
        else:
            st.success(f'Rendered in {render_time} seconds', icon="✅")
            with open(f'file.{out}', "rb") as file:
                btn = st.download_button(
                        label=f"Download {out}",
                        data=file,
                        file_name=f'TextTango_{text1}_{text2}.{out}',
                        mime=f"model/{out}"
                    )
            st.markdown("Post the make [on Printables](https://www.printables.com/it/model/520333-texttango-dual-letter-illusion) to support the project!", unsafe_allow_html=True)
            st.markdown("I am a student who enjoys 3D printing and programming. To support me with a coffee, just [click here!](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)", unsafe_allow_html=True)

            # stl preview
            stl_from_file('file_display.stl')