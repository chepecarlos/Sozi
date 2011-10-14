
import os
import sys
import inkex


SOZI_VERSION = "{{SOZI_VERSION}}"


def upgrade_or_install(context):
    upgrade_or_install_element(context, "script", "js")
    upgrade_document(context)
    

def upgrade_or_install_element(context, tag, ext):
    # Check version and remove older versions
    latest_version_found = False
    for elt in context.document.xpath("//svg:" + tag + "[@id='sozi-extras-addvideo-" + tag + "']", namespaces=inkex.NSS):
        version = elt.attrib[inkex.addNS("version", "sozi")]
        if version == SOZI_VERSION:
            latest_version_found = True
        elif version < SOZI_VERSION:
            elt.getparent().remove(elt)
        else:
            sys.stderr.write("Document has been created using a higher version of Sozi. Please upgrade the Inkscape plugin.\n")
            exit()
  
    # Create new element if needed
    if not latest_version_found:
        elt = inkex.etree.Element(inkex.addNS(tag, "svg"))
        elt.text = open(os.path.join(os.path.dirname(__file__), "sozi_extras_addvideo." + ext)).read()
        elt.set("id","sozi-extras-addvideo-" + tag)
        elt.set(inkex.addNS("version", "sozi"), SOZI_VERSION)
        context.document.getroot().append(elt)


def upgrade_document(context):
    # Upgrade from 11.10
    auto_attr = inkex.addNS("auto", "sozi")
    frame_attr = inkex.addNS("frame", "sozi")
    start_frame_attr = inkex.addNS("start-frame", "sozi")
    stop_frame_attr = inkex.addNS("stop-frame", "sozi")
    frame_count = len(context.document.xpath("//sozi:frame", namespaces=inkex.NSS))
    
    # For each video element in the document
    for velt in context.document.xpath("//sozi:video", namespaces=inkex.NSS):
        # Get the Sozi frame index for the current video if it is set
        frame_index = None
        if frame_attr in velt.attrib:
            frame_index = velt.attrib[frame_attr]
            del velt.attrib[frame_attr]
        
        # If the video was set to start automatically and has a frame index set
        if auto_attr in velt.attrib:
            if velt.attrib[auto_attr] == "true" and frame_index is not None:
                # Get the frame element at the given index
                felt = context.document.xpath("//sozi:frame[@sozi:sequence='" + frame_index + "']", namespaces=inkex.NSS)
                if len(felt) > 0:
                    # Use the ID of that frame to start the video
                    velt.set(start_frame_attr, felt[0].attrib["id"])
                    
                    # Get the next frame element
                    # We assume that the frames are correctly numbered                        
                    if int(frame_index) >= frame_count:
                        frame_index = "1"
                    else:
                        frame_index = unicode(int(frame_index) + 1)
                    felt = context.document.xpath("//sozi:frame[@sozi:sequence='" + frame_index + "']", namespaces=inkex.NSS)
                    if len(felt) > 0:
                        # Use the ID of that frame to stop the video
                        velt.set(stop_frame_attr, felt[0].attrib["id"])
            del velt.attrib[auto_attr]                

        # If the video has attributes "type" and "src" with no namespace, add Sozi namespace
        if "type" in velt.attrib:
            velt.set(inkex.addNS("type", "sozi"), velt.attrib["type"])
            del velt.attrib["type"]
            
        if "src" in velt.attrib:
            velt.set(inkex.addNS("src", "sozi"), velt.attrib["src"])
            del velt.attrib["src"]
