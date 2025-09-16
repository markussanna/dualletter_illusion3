import cadquery as cq
import math
from typing import List, Tuple
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
def create_text_object(text="Love", font_size=10, font_path='', 
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
        .text(text, font_size, text_height, fontPath=font_path)
        .rotate((0, 0, 0), (0, 0, 1), 270)  # Rotate 90 degrees around Z-axis
        .translate(position)
    )
    
    return text_obj
def create_heart_with_text(heart_height=1.0, thickness=0.1, height=1.5, 
                          text="Love", font_size=100, font_path='', 
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
    text_obj = create_text_object_with_debug(
        text=text,
        font_size=font_size,
        font_path=font_path,
        text_height=text_height,
        position=(center_x, center_y, text_z),
        bridge_height=3,
        bridge_diameter=3,
        debug=True
    )
    
    # Combine heart and text
    result = heart.union(text_obj)
    
    return result


def create_text_object_with_bridges(text="Love", font_size=10, font_path='', 
                                  text_height=0.5, position=(0, 0, 0),
                                  bridge_height=0.05, bridge_width=0.3):
    """
    Create a 3D text object with bridges for characters that have dots.
    
    Parameters:
    text (str): Text to create
    font_size (float): Font size for the text
    font_path (str): Path to font file
    text_height (float): Extrusion height of the text
    position (tuple): Position (x, y, z) to place the text
    bridge_height (float): Height of the bridge (typically 10% of text_height)
    bridge_width (float): Width of the bridge connections
    
    Returns:
    cq.Workplane: A 3D text object with bridges
    """
    # Characters that typically have dots above them
    dotted_chars = ['i', 'j', 'ö', 'ä', 'ü', 'ï', 'İ', 'ĳ', 'ĭ', 'ı']
    
    # Create the main text object
    text_obj = (
        cq.Workplane("XY")
        .text(text, font_size, text_height, fontPath=font_path)
        .rotate((0, 0, 0), (0, 0, 1), 270)  # Rotate 90 degrees around Z-axis
    )
    
    # Find positions where we might need bridges
    for i, char in enumerate(text):
        if char.lower() in [c.lower() for c in dotted_chars]:
            # Estimate position of this character (approximate based on font size)
            char_x_offset = i * font_size * 0.6  # Rough estimate, may need adjustment
            
            # Create a small bridge at this position
            # This is a simplified approach - you might want to use more precise positioning
            bridge = (
                cq.Workplane("XY")
                .rect(bridge_width, bridge_width)  # Square bridge
                .extrude(bridge_height)
                .translate((char_x_offset, font_size * 0.7, text_height - bridge_height))
            )
            
            # Add the bridge to the main text
            text_obj = text_obj.union(bridge)
    
    # Apply final translation
    text_obj = text_obj.translate(position)
    
    return text_obj

# Alternative: More precise method using bounding boxes
def create_text_object_precise_bridges(text="Love", font_size=10, font_path='', 
                                     text_height=0.5, position=(0, 0, 0),
                                     bridge_height=0.05, bridge_diameter=0.4):
    """
    More precise method that analyzes the geometry to find dots and add bridges.
    """
    # Create the main text
    text_obj = (
        cq.Workplane("XY")
        .text(text, font_size, text_height, fontPath=font_path)
        .rotate((0, 0, 0), (0, 0, 1), 270)
    )
    
    # Get all solids and analyze them
    solids = text_obj.solids().vals()
    
    for solid in solids:
        # Get bounding box to determine if this might be a dot
        bbox = solid.BoundingBox()
        width = bbox.xlen
        height = bbox.ylen
        depth = bbox.zlen
        
        # Dots are typically small and positioned above the main text
        if (width < font_size * 0.3 and height < font_size * 0.3 and 
            bbox.ymax > font_size * 0.4):  # Dots are usually high on Y-axis
            
            # Find the center of the dot
            dot_center = ((bbox.xmin + bbox.xmax) / 2, 
                         (bbox.ymin + bbox.ymax) / 2, 
                         (bbox.zmin + bbox.zmax) / 2)
            
            # Find the nearest main character part (simplified approach)
            # Look for the closest point in the main text body
            main_body_center = (dot_center[0], dot_center[1] - font_size * 0.3, dot_center[2])
            
            # Create a cylindrical bridge between dot and main body
            bridge_vector = (main_body_center[0] - dot_center[0],
                           main_body_center[1] - dot_center[1],
                           main_body_center[2] - dot_center[2])
            
            bridge_length = math.sqrt(bridge_vector[0]**2 + bridge_vector[1]**2 + bridge_vector[2]**2)
            
            if bridge_length > 0:
                # Create a cylinder bridge
                bridge = (
                    cq.Workplane("XY")
                    .circle(bridge_diameter / 2)
                    .extrude(bridge_length)
                    .translate((0, 0, -bridge_length / 2))
                    .rotate((0, 0, 0), (0, 1, 0), -math.degrees(math.atan2(bridge_vector[0], bridge_vector[2])))
                    .rotate((0, 0, 0), (1, 0, 0), math.degrees(math.atan2(bridge_vector[1], math.sqrt(bridge_vector[0]**2 + bridge_vector[2]**2))))
                    .translate(dot_center)
                )
                
                text_obj = text_obj.union(bridge)
    
    return text_obj.translate(position)

def create_text_object_with_debug(text="äöi", font_size=100, font_path='', 
                                 text_height=10, position=(0, 0, 0),
                                 bridge_height=1.0, bridge_diameter=4.0,
                                 debug=False):
    """
    Create a 3D text object with bridges between dots and their base characters.
    Includes debugging visualization.
    """
    # Create the main text
    text_obj = (
        cq.Workplane("XY")
        .text(text, font_size, text_height, fontPath=font_path)
        .rotate((0, 0, 0), (0, 0, 1), 270)
    )
    
    if debug:
        print(f"Processing text: '{text}'")
        print(f"Font size: {font_size}, Text height: {text_height}")
    
    # Get all solids and analyze them
    solids = text_obj.solids().vals()
    
    if debug:
        print(f"Found {len(solids)} solids in the text")
    
    # Calculate average character size for better detection
    avg_width = sum(solid.BoundingBox().xlen for solid in solids) / len(solids)
    avg_height = sum(solid.BoundingBox().ylen for solid in solids) / len(solids)
    
    if debug:
        print(f"Average character size: {avg_width:.2f} x {avg_height:.2f}")
    
    # Separate dots from main characters
    dots = []
    main_chars = []
    
    for i, solid in enumerate(solids):
        bbox = solid.BoundingBox()
        width = bbox.xlen
        height = bbox.ylen
        depth = bbox.zlen
        center = ((bbox.xmin + bbox.xmax) / 2, 
                 (bbox.ymin + bbox.ymax) / 2, 
                 (bbox.zmin + bbox.zmax) / 2)
        
        if debug:
            print(f"Solid {i}: center={center}, size=({width:.2f}, {height:.2f}, {depth:.2f}), ymax={bbox.ymax:.2f}")
        
        # Much more lenient dot detection criteria
        # Look for small, isolated elements that could be dots
        is_dot = (width < avg_width * 0.4 and    # Significantly smaller than average width
                 height < avg_height * 0.4 and   # Significantly smaller than average height
                 depth == text_height and        # Same depth as text
                 width > 0.1 and height > 0.1)   # Not just a line or artifact
        
        if is_dot:
            dots.append((solid, center, bbox))
            if debug:
                print(f"  → Identified as DOT (size ratio: {width/avg_width:.2f}, {height/avg_height:.2f})")
        else:
            main_chars.append((solid, center, bbox))
            if debug:
                print(f"  → Identified as MAIN CHARACTER")
    
    if debug:
        print(f"Found {len(dots)} dots and {len(main_chars)} main characters")
        for i, (dot, center, bbox) in enumerate(dots):
            print(f"Dot {i}: center={center}, size=({bbox.xlen:.2f}, {bbox.ylen:.2f})")
    
    # For each dot, find the closest main character and create a bridge
    debug_objects = []
    bridges_created = 0
    
    for dot_solid, dot_center, dot_bbox in dots:
        if debug:
            print(f"\nProcessing dot at {dot_center}")
        
        # Find the closest main character to this dot
        closest_char = None
        min_distance = float('inf')
        
        for char_solid, char_center, char_bbox in main_chars:
            # Calculate distance (consider both position and size)
            distance = math.sqrt((char_center[0] - dot_center[0])**2 + 
                                (char_center[1] - dot_center[1])**2)
            
            # Also check if this character is likely to be the base (should be below the dot)
            is_likely_base = (char_center[1] < dot_center[1] and  # Character is below dot
                             abs(char_center[0] - dot_center[0]) < font_size * 0.8)  # Horizontally aligned
            
            if debug:
                print(f"  Distance to main char at {char_center}: {distance:.2f}, likely base: {is_likely_base}")
            
            if is_likely_base and distance < min_distance:
                min_distance = distance
                closest_char = (char_solid, char_center, char_bbox)
        
        if closest_char and min_distance < font_size * 2:
            char_solid, char_center, char_bbox = closest_char
            
            if debug:
                print(f"  Closest main character at {char_center}, distance: {min_distance:.2f}")
            
            # Find connection points - dot bottom and character top
            dot_bottom = (dot_center[0], dot_bbox.ymin, text_height / 2)
            char_top = (char_center[0], char_bbox.ymax, text_height / 2)
            
            # Create a bridge between dot bottom and character top
            bridge_vector = (char_top[0] - dot_bottom[0],
                           char_top[1] - dot_bottom[1],
                           char_top[2] - dot_bottom[2])
            
            bridge_length = math.sqrt(bridge_vector[0]**2 + bridge_vector[1]**2 + bridge_vector[2]**2)
            
            if bridge_length > 0 and bridge_length < font_size * 2:
                if debug:
                    print(f"  Creating bridge of length {bridge_length:.2f} from {dot_bottom} to {char_top}")
                
                # Create cylindrical bridge
                bridge = (
                    cq.Workplane("XY")
                    .circle(bridge_diameter / 2)
                    .extrude(bridge_length)
                    .translate((0, 0, -bridge_length / 2))
                    .rotate((0, 0, 0), (0, 1, 0), -math.degrees(math.atan2(bridge_vector[0], bridge_vector[2])))
                    .rotate((0, 0, 0), (1, 0, 0), math.degrees(math.atan2(bridge_vector[1], math.sqrt(bridge_vector[0]**2 + bridge_vector[2]**2))))
                    .translate(dot_bottom)
                )
                
                text_obj = text_obj.union(bridge)
                bridges_created += 1
                
                if debug:
                    # Create debug visualization
                    debug_sphere = (
                        cq.Workplane("XY")
                        .sphere(bridge_diameter)
                        .translate(dot_bottom)
                        .translate((0, 0, text_height + 2))  # Offset to avoid interference
                    )
                    debug_objects.append(debug_sphere)
    
    if debug:
        print(f"Created {bridges_created} bridges")
    
    # Add debug objects if enabled
    if debug and debug_objects:
        debug_obj = debug_objects[0]
        for obj in debug_objects[1:]:
            debug_obj = debug_obj.union(obj)
        text_obj = text_obj.union(debug_obj)
    
    return text_obj.translate(position)

# Test with your specific case
if __name__ == "__main__":
    text_with_bridges = create_text_object_with_debug(
        text="äöi", 
        font_size=100, 
        text_height=10, 
        bridge_height=1.0,
        bridge_diameter=4.0,
        debug=True
    )
    
    # Export for inspection
    cq.exporters.export(text_with_bridges, "debug_text_with_bridges.stl")
    print("Exported to debug_text_with_bridges.stl")

def export_debug_view(text_obj, filename="debug_text.stl"):
    """Export the text object for debugging"""
    cq.exporters.export(text_obj, filename)
    print(f"Debug view exported to {filename}")
    
def create_text_object_with_tunable_params(text="üäöi", font_size=100, font_path='', 
                                         text_height=10, position=(0, 0, 0),
                                         bridge_height=1.0, bridge_diameter=4.0,
                                         # Tunable parameters for dot detection
                                         dot_size_ratio=0.4,    # Max size relative to average
                                         dot_min_size=5.0,      # Minimum size to be considered a dot
                                         dot_max_size=20.0,     # Maximum size to be considered a dot
                                         # Tunable parameters for base detection
                                         max_horizontal_offset=80.0,  # Max horizontal distance
                                         max_vertical_distance=150.0, # Max vertical distance
                                         require_below_dot=True,      # Base must be below dot
                                         debug=False):
    """
    Create a 3D text object with bridges between dots and their base characters.
    Includes tunable parameters for fine-tuning.
    """
    # Create the main text
    text_obj = (
        cq.Workplane("XY")
        .text(text, font_size, text_height, fontPath=font_path)
        .rotate((0, 0, 0), (0, 0, 1), 270)
    )
    
    if debug:
        print(f"Processing text: '{text}'")
        print(f"Font size: {font_size}, Text height: {text_height}")
        print(f"Tunable params: dot_size_ratio={dot_size_ratio}, dot_min_size={dot_min_size}, "
              f"dot_max_size={dot_max_size}, max_horizontal_offset={max_horizontal_offset}")
    
    # Get all solids and analyze them
    solids = text_obj.solids().vals()
    
    if debug:
        print(f"Found {len(solids)} solids in the text")
    
    # Calculate average character size for better detection
    if solids:
        avg_width = sum(solid.BoundingBox().xlen for solid in solids) / len(solids)
        avg_height = sum(solid.BoundingBox().ylen for solid in solids) / len(solids)
    else:
        avg_width, avg_height = font_size, font_size
    
    if debug:
        print(f"Average character size: {avg_width:.2f} x {avg_height:.2f}")
    
    # Separate dots from main characters
    dots = []
    main_chars = []
    
    for i, solid in enumerate(solids):
        bbox = solid.BoundingBox()
        width = bbox.xlen
        height = bbox.ylen
        depth = bbox.zlen
        center = ((bbox.xmin + bbox.xmax) / 2, 
                 (bbox.ymin + bbox.ymax) / 2, 
                 (bbox.zmin + bbox.zmax) / 2)
        
        if debug:
            print(f"Solid {i}: center={center}, size=({width:.2f}, {height:.2f}, {depth:.2f}), ymax={bbox.ymax:.2f}")
        
        # Tunable dot detection criteria
        size_ratio_ok = (width < avg_width * dot_size_ratio and 
                        height < avg_height * dot_size_ratio)
        absolute_size_ok = (width > dot_min_size and height > dot_min_size and
                           width < dot_max_size and height < dot_max_size)
        depth_ok = (depth == text_height)
        
        is_dot = size_ratio_ok and absolute_size_ok and depth_ok
        
        if is_dot:
            dots.append((solid, center, bbox))
            if debug:
                print(f"  → Identified as DOT (size ratio: {width/avg_width:.2f}, {height/avg_height:.2f})")
        else:
            main_chars.append((solid, center, bbox))
            if debug:
                print(f"  → Identified as MAIN CHARACTER")
    
    if debug:
        print(f"Found {len(dots)} dots and {len(main_chars)} main characters")
        for i, (dot, center, bbox) in enumerate(dots):
            print(f"Dot {i}: center={center}, size=({bbox.xlen:.2f}, {bbox.ylen:.2f})")
    
    # For each dot, find the closest main character and create a bridge
    debug_objects = []
    bridges_created = 0
    
    for dot_solid, dot_center, dot_bbox in dots:
        if debug:
            print(f"\nProcessing dot at {dot_center}")
        
        # Find the closest main character to this dot
        closest_char = None
        min_distance = float('inf')
        
        for char_solid, char_center, char_bbox in main_chars:
            # Calculate distances
            horizontal_distance = abs(char_center[0] - dot_center[0])
            vertical_distance = char_center[1] - dot_center[1]  # Negative if char is below dot
            
            # Check if this character could be the base
            horizontal_ok = horizontal_distance < max_horizontal_offset
            vertical_ok = (not require_below_dot or vertical_distance < 0)  # Below dot if required
            distance_ok = math.sqrt(horizontal_distance**2 + vertical_distance**2) < max_vertical_distance
            
            if horizontal_ok and vertical_ok and distance_ok:
                distance = math.sqrt(horizontal_distance**2 + vertical_distance**2)
                
                if debug:
                    print(f"  Potential base at {char_center}: dist={distance:.2f}, "
                          f"h={horizontal_distance:.2f}, v={vertical_distance:.2f}")
                
                if distance < min_distance:
                    min_distance = distance
                    closest_char = (char_solid, char_center, char_bbox)
        
        if closest_char:
            char_solid, char_center, char_bbox = closest_char
            
            if debug:
                print(f"  Selected base at {char_center}, distance: {min_distance:.2f}")
            
            # Find connection points - dot bottom and character top
            dot_bottom = (dot_center[0], dot_bbox.ymin, text_height / 2)
            char_top = (char_center[0], char_bbox.ymax, text_height / 2)
            
            # Create a bridge between dot bottom and character top
            bridge_vector = (char_top[0] - dot_bottom[0],
                           char_top[1] - dot_bottom[1],
                           char_top[2] - dot_bottom[2])
            
            bridge_length = math.sqrt(bridge_vector[0]**2 + bridge_vector[1]**2 + bridge_vector[2]**2)
            
            if bridge_length > 0 and bridge_length < max_vertical_distance:
                if debug:
                    print(f"  Creating bridge of length {bridge_length:.2f} from {dot_bottom} to {char_top}")
                
                # Create cylindrical bridge
                bridge = (
                    cq.Workplane("XY")
                    .circle(bridge_diameter / 2)
                    .extrude(bridge_length)
                    .translate((0, 0, -bridge_length / 2))
                    .rotate((0, 0, 0), (0, 1, 0), -math.degrees(math.atan2(bridge_vector[0], bridge_vector[2])))
                    .rotate((0, 0, 0), (1, 0, 0), math.degrees(math.atan2(bridge_vector[1], math.sqrt(bridge_vector[0]**2 + bridge_vector[2]**2))))
                    .translate(dot_bottom)
                )
                
                text_obj = text_obj.union(bridge)
                bridges_created += 1
                
                if debug:
                    # Create debug visualization
                    debug_sphere = (
                        cq.Workplane("XY")
                        .sphere(bridge_diameter)
                        .translate(dot_bottom)
                        .translate((0, 0, text_height + 2))
                    )
                    debug_objects.append(debug_sphere)
    
    if debug:
        print(f"Created {bridges_created} bridges")
    
    # Add debug objects if enabled
    if debug and debug_objects:
        debug_obj = debug_objects[0]
        for obj in debug_objects[1:]:
            debug_obj = debug_obj.union(obj)
        text_obj = text_obj.union(debug_obj)
    
    return text_obj.translate(position)

def test_parameters():
    test_text = "üäöi"
    
    # Try different parameter combinations
    parameter_sets = [
        {"dot_size_ratio": 0.3, "dot_min_size": 10.0, "dot_max_size": 20.0, "max_horizontal_offset": 50.0},
        {"dot_size_ratio": 0.4, "dot_min_size": 5.0, "dot_max_size": 25.0, "max_horizontal_offset": 80.0},
        {"dot_size_ratio": 0.5, "dot_min_size": 1.0, "dot_max_size": 30.0, "max_horizontal_offset": 100.0},
        {"dot_size_ratio": 0.6, "dot_min_size": 1.0, "dot_max_size": 40.0, "max_horizontal_offset": 120.0, "require_below_dot": False},
    ]
    
    for i, params in enumerate(parameter_sets):
        print(f"\n{'='*60}")
        print(f"Testing parameter set {i+1}: {params}")
        print(f"{'='*60}")
        
        text_obj = create_text_object_with_tunable_params(
            text=test_text,
            font_size=100,
            text_height=10,
            bridge_height=1.0,
            bridge_diameter=4.0,
            debug=True,
            **params
        )
        
        cq.exporters.export(text_obj, f"test_params_{i+1}.stl")
        print(f"Exported to test_params_{i+1}.stl")

   