import cadquery as cq

def create_hollow_heart(heart_height=1.0, thickness=0.1, height=1.5):
    
    factor = heart_height/5
    """
    Create a hollow heart shape with consistent wall thickness.
    
    Parameters:
    factor (float): Scaling factor for the heart size
    thickness (float): Wall thickness of the heart
    height (float): Height (extrusion depth) of the heart
    
    Returns:
    cq.Workplane: A hollow heart shape
    """
    # Create the outer heart
    outer = (
        cq.Workplane("XY")
        .lineTo(2*factor, 2*factor)
        .threePointArc((4*factor, factor), (3.5*factor, 0))
        .mirrorX()
        .extrude(-height)
    )
    
    # Create the inner heart (offset from outer)
    inner = (
        cq.Workplane("XY")
        .lineTo(2*factor, 2*factor)
        .threePointArc((4*factor, factor), (3.5*factor, 0))
        .mirrorX()
        .offset2D(-thickness, kind="intersection")
        .extrude(-height)
    )
    
    # Subtract inner from outer to create hollow heart
    heart = outer - inner
    
    
    return heart
def create_text_object(text="Love", font_size=10, font_name="Arial", 
                      text_height=0.5, position=(0, 0, 0)):
    """
    Create a 3D text object.
    
    Parameters:
    text (str): Text to create
    font_size (float): Font size for the text
    font_name (str): Font name for the text
    text_height (float): Extrusion height of the text
    position (tuple): Position (x, y, z) to place the text
    
    Returns:
    cq.Workplane: A 3D text object
    """
    text_obj = (
        cq.Workplane("XY")
        .text(text, font_size, text_height, fontPath=font_name)
        .rotate((0, 0, 0), (0, 0, 1), 270)  # Rotate 90 degrees around Z-axis
        .translate(position)
    )
    
    return text_obj
def create_heart_with_text(heart_height=1.0, thickness=0.1, height=1.5, 
                          text="Love", font_size=100, font_name="Arial", 
                          text_height=0.5, text_offset=0.0):
    """
    Create a hollow heart shape with text in the center.
    
    Parameters:
    factor (float): Scaling factor for the heart size
    thickness (float): Wall thickness of the heart
    height (float): Height (extrusion depth) of the heart
    text (str): Text to place in the center of the heart
    font_size (float): Font size for the text
    font_name (str): Font name for the text
    text_height (float): Extrusion height of the text
    text_offset (float): Z-offset for the text (above the heart surface)
    
    Returns:
    cq.Workplane: A heart shape with text in the center
    """
    # Create the hollow heart
    heart = create_hollow_heart(heart_height, thickness, height)
    
    bbHeart = heart.val().BoundingBox()
    length = bbHeart.xlen
    width = bbHeart.ylen
    height = bbHeart.zlen
    # Calculate center position for the text
    center_x = length/2  # Heart is symmetric around X-axis
    center_y = width/2  # Approximate center in Y direction
    text_z = - text_height # Position text slightly above heart surface
    
    # Create the text object
    text_obj = create_text_object(
        text=text,
        font_size=font_size,
        font_name=font_name,
        text_height=text_height,
        position=(center_x, center_y, text_z)
    )
    
    # Combine heart and text
    result = heart.union(text_obj)
    
    return result


#heart = create_hollow_heart(width=10.0, thickness=0.1, height=1.5)
#text = create_text_object(text="Love", font_size=10, font_name="Arial", 
 #                        text_height=0.5, position=(0, 1, 0.1))
 