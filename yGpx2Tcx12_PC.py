import gpxpy
import xml.etree.ElementTree as ET
from xml.dom import minidom
from haversine import haversine, Unit
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import io
#import tkinter.filedialog
import os
import re
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog

def open_file_dialog():
    app = QApplication(sys.argv)

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setViewMode(QFileDialog.Detail)  # User can sort by column (e.g., date)
    dialog.setOption(QFileDialog.DontUseNativeDialog, False)
    dialog.setNameFilter("Gpx Files (*.gpx)")

    selected_files = []
    if dialog.exec_():
        selected_files = dialog.selectedFiles()

    return selected_files


def isAscending(xs):
    for n in range(len(xs) - 1):
        if xs[n] > xs[n+1]:
            return False
    return True

def find_line_number(file_path, target_string):
    with open(file_path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if target_string in line:
                return line_number
    return None

def gpx_to_tcx(gpx_file, tcx_file):
    global poiarray
    poiarray=np.array([])
    global gltime
    gltime=np.array([])
    global distpp# = np.array([], dtype=float)
    distpp=np.array([])
    global timeseries
    timeseries=np.array([])
    global poitime
    poitime=np.array([])
    global distf
    global tti

    with open(gpx_file, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
#    # Parse the GPX file
#    with open(gpx_file, 'r') as f:
#        gpx = gpxpy.parse(f)

    # Create the root element of the TCX file
    tcx = ET.Element('TrainingCenterDatabase', xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    folders = ET.SubElement(tcx, 'Folders')
    courses = ET.SubElement(folders, 'Courses')
    coursefolder = ET.SubElement(courses, 'CourseFolder', Name='Courses')  # Change sport as needed
    courseNameRef = ET.SubElement(coursefolder, 'CourseNameRef')  # Change sport as needed
    id = ET.SubElement(courseNameRef, 'Id')  # Change sport as needed
    id.text = "Oko"
    courses = ET.SubElement(tcx, 'Courses')
    course = ET.SubElement(courses, 'Course')  # Change sport as needed

    # Find the first timestamp in the GPX file for the activity ID
    first_timestamp = None
    for track in gpx.tracks:
        for segment in track.segments:
            if segment.points:
                first_timestamp = segment.points[0].time
                break
        if first_timestamp:
            break
    
#    id_element = ET.SubElement(course, 'Id')
#    id_element.text = first_timestamp.isoformat() if first_timestamp else '2025-01-23T00:00:00Z'  # Default timestamp if not found

    # Loop through each track in the GPX file and convert them to TCX format
    name = ET.SubElement(course, 'Name')
    name.text = "text"

    lap = ET.SubElement(course, 'Lap')
    totaltimeseconds= ET.SubElement(lap, 'TotalTimeSeconds')
    totaltimeseconds.text= ''#str(2261)
#    lap_id = ET.SubElement(lap, 'Id')
#    lap_id.text = '1'
    distancemeters= ET.SubElement(lap, 'DistanceMeters')
    distancemeters.text = ''#str(41788.0)
    beginposition= ET.SubElement(lap, 'BeginPosition')
    latitudedegrees= ET.SubElement(beginposition,'LatitudeDegrees')
    longitudedegrees=ET.SubElement(beginposition,'LongitudeDegrees')
    endposition=ET.SubElement(lap,'EndPosition')
    latitudedegrees=ET.SubElement(endposition,'LatitudeDegrees')
    longitudedegrees=ET.SubElement(endposition,'LongitudeDegrees')
    intensity=ET.SubElement(lap,'Intensity')
    intensity.text="Active"

    
 #   lap_start_time = ET.SubElement(lap, 'StartTime')
 #   lap_start_time.text = first_timestamp.isoformat() if first_timestamp else '2025-01-23T00:00:00Z'

    track = ET.SubElement(course, 'Track')
    flag = True
    dist = 0
    i=0
    timestamp = first_timestamp.isoformat() if first_timestamp else '2025-01-23T00:00:00Z'
    for track_segment in gpx.tracks[0].segments:
        for point in track_segment.points:
            i+=1
            track_point = ET.SubElement(track, 'Trackpoint')
            time = ET.SubElement(track_point, 'Time')
            timestamp = time.isoformat() if time else '2025-01-23T00:00:00Z'
            timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            timestamp = timestamp + timedelta(seconds=10*(i-1))
            gltime=np.append(gltime,timestamp)
            poitime=np.append(poitime,timestamp)
            timeseries = np.append(timeseries, timestamp)
            timestamp_str = timestamp.isoformat() + "Z"
            time.text = timestamp_str
            position = ET.SubElement(track_point, 'Position')
            latitude = ET.SubElement(position, 'LatitudeDegrees')
            latitude.text = str(point.latitude)
            longitude = ET.SubElement(position, 'LongitudeDegrees')
            longitude.text = str(point.longitude)
            altitude = ET.SubElement(track_point, 'AltitudeMeters')
            altitude.text = str(point.elevation)

            if flag:
                flag = False
            else:
                lyon = (plat, plon)
                paris = (point.latitude, point.longitude)
                disttmp = haversine(lyon,paris)*1000
                dist= dist+disttmp
#                print(disttmp,dist)
            plat = point.latitude
            plon = point.longitude

            distance = ET.SubElement(track_point, 'DistanceMeters')
#            distance.text = str(dist)
            distance.text = str(format(dist, '.2f'))
            poiarray=np.append(poiarray,[point.latitude,point.longitude,dist])
#            distdata=np.append(distdata,dist)


#            heart_rate = ET.SubElement(track_fxpoint, 'HeartRateBpm')
#            heart_rate_value = ET.SubElement(heart_rate, 'Value')
#            heart_rate_value.text = '0'  # Modify this if heart rate data is available in GPX
        distf = format(dist, '.2f')
        tti = i
    # Use minidom to prettify the XML output
    rough_string = ET.tostring(tcx, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write the prettified TCX file
    with open(tcx_file, 'w') as f:
        f.write(pretty_xml)
    f.close()

def printcp(lat,lon,name1,desc,poitype,time,num,cp0,cp1):#,time):
    timestr = time.isoformat()+"Z"
    print("      <CoursePoint>"                                                           , file=memory_file)
    print(f"        <Name>{list(name1[num])[0]}</Name>"                                             , file=memory_file)
    print(f"          <Time>{timestr}</Time>"                                                , file=memory_file)
    print("          <Position>"                                                          , file=memory_file)
    print(f"            <LatitudeDegrees>{cp0}</LatitudeDegrees>"                         , file=memory_file)
    print(f"            <LongitudeDegrees>{cp1}</LongitudeDegrees>"                       , file=memory_file)
    print("          </Position>"                                                         , file=memory_file)
#    print(f"          <DistanceMeters>{cpdist_str}</DistanceMeters>"                      , file=memory_file)
#    print(f"        <PointType>{sym.text if sym is not None else 'N/A'}</PointType>"      , file=memory_file)
    print(f"        <PointType>{poitype}</PointType>"      , file=memory_file)
    print(f"        <Notes>{desc.text if desc is not None else 'none'}</Notes>"                                                , file=memory_file)
    print("      </CoursePoint>"                                                          , file=memory_file)

###########################################################
### start of the program
###########################################################
# Create an in-memory file-like object
memory_file = io.StringIO()

## #input_file = tkinter.filedialog.askopenfilename(filetypes=[("gpxfile", "*.gpx")])
## idir = r'C:\Users\J0155879\OneDrive - Honda\etc\bici\コース\gpx'
## flts=[("", "*.gpx")]
## # Open file dialog to select multiple files
## file_paths = tkinter.filedialog.askopenfilenames(title="Select tcxfiles",filetypes = flts, initialdir = idir)

file_paths = open_file_dialog()
# Process each file
for file_path in file_paths:
    print(f"Processing: {file_path}")
    #input_file = tkinter.filedialog.askopenfilename(filetypes = flts, initialdir = idir)#"*.gpx *.tcx"
    basename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
    print(basename_without_ext)
    dirname = os.path.dirname(file_path)
    output_file2 = dirname+"/"+'o'+basename_without_ext+".tcx"

    #output_file = "tmp.tcx"
    # Example usage
    gpx_to_tcx(file_path, output_file2)

    # Parse the GPX file
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Namespace for GPX (may vary depending on the file)
    namespace = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    # Extract all <wpt> elements
    waypoints = root.findall('gpx:wpt', namespace)
    # Iterate through waypoints and print their details
    poiarray = np.reshape(poiarray,(-1,3))
    [mm,nn]=poiarray.shape
    time="2025-01-12T11:57:48Z"

    for wpt in waypoints:#fist time
        lat = wpt.get('lat')
        lon = wpt.get('lon')
        name = wpt.find('gpx:name', namespace)
        cmt = wpt.find('gpx:cmt', namespace)
        desc = wpt.find('gpx:desc', namespace)
        sym = wpt.find('gpx:sym', namespace)
        print(f"Waypoint: Latitude={lat}, Longitude={lon}, Name={name.text if name is not None else 'N/A'}, Sym={sym.text if sym is not None else 'N/A'}")
        latf = float(lat)
        lonf = float(lon)
        lyon=(latf, lonf)
        for m in range(mm):
            paris=(poiarray[m,0],poiarray[m,1])
            distpp=np.append(distpp,(haversine(lyon,paris)))

    [mm,nn]=poiarray.shape
    distpp = np.reshape(distpp,(-1,mm))
    [mmm,nnn] = distpp.shape

    ##plot graph for waypoint distance 
    #for i in range(mmm):
    #    plt.plot(distpp[i,:], label=i)
    #    plt.legend()
    #plt.show()

    distppamin=np.argmin(distpp, axis=1)
    distppamin2=sorted(distppamin)
    distppamin2 = [int(x) for x in distppamin2]
    print(distppamin2)
    if isAscending(distppamin[:]):
        print("Ascending order")
    else:
        print("Not ascending order")
    #cp2=poiarray[distppamin2,2]
    #poitime2=poitime[distppamin2]
    cp0=poiarray[distppamin,0]
    cp1=poiarray[distppamin,1]
    #cp2=poiarray[distppamin,2]
    poitime2=poitime[distppamin]
    #waypoint2=[x for _, x in zip(sorted(distppamin2),waypoints)]
    name1=np.array([])
    cmt1 = np.array([])
    desc1 = np.array([])
#    sym1 = np.array([])
    for wpt in waypoints:#inbetween first and second
        lat = wpt.get('lat')
        lon = wpt.get('lon')
        name = wpt.find('gpx:name', namespace)
        cmt = wpt.find('gpx:cmt', namespace)
        desc = wpt.find('gpx:desc', namespace)
#        sym = wpt.find('gpx:sym', namespace)
        sym={wpt.find('gpx:sym', namespace) if sym is not None else 'N/A'}
    #    print(f"Waypoint: Latitude={lat}, Longitude={lon}, Name={name.text if name is not None else 'N/A'}, Sym={sym.text if sym is not None else 'N/A'}")
#        symtmp = {sym.text if sym.text is not None else 'void'}
        name1 = np.append(name1,{name.text if name is not None else 'none'})     # you can use other variable name if you want to.
        cmt1 = np.append(cmt1,{cmt.text if cmt is not None else 'none'})     # you can use other variable name if you want to.
        desc1 = np.append(desc1,{desc.text if desc is not None else 'none'})     # you can use other variable name if you want to.
#        sym1 = np.append(sym1,symtmp)     # you can use other variable name if you want to.

    wpti=0
    for wpt in waypoints:#second time
        lat = wpt.get('lat')
        lon = wpt.get('lon')
        cmt = wpt.find('gpx:cmt', namespace)
        desc = wpt.find('gpx:desc', namespace)
        sym = wpt.find('gpx:sym', namespace)
        poitype = 'Generic'
        if sym is not None and sym.text is not None:
            if ('Gas' in sym.text or 'Restaurant' in sym.text or 'Convenience Store' in sym.text):
                poitype = 'Food'
            elif ('Water' in sym.text or 'Water Source' in sym.text):
                poitype = 'Water'
            elif ('Tunnel' in sym.text):
                poitype = 'Danger'
            else:
                poitype = 'Generic'
        print(f"Waypoint: Latitude={lat}, Longitude={lon}, Name={name1[wpti] if name1[wpti] is not None else 'N/A'}, Desc={desc1[wpti] if desc1[wpti] is not None else 'N/A'}, Sym={poitype if poitype is not None else 'N/A'}")
        note = wpt.find('gpx:note', namespace)
        printcp(lat,lon,name1,desc,poitype,poitime2[wpti],wpti,cp0[wpti],cp1[wpti])
        wpti+=1

    memory_file.seek(0)

    # Read and display the contents
    contents = memory_file.read()
    print("Contents of the memory file:")
    with open(output_file2, 'r') as file:
        content = file.read()
    # Find all occurrences of </Track> and insert text after them
    new_content = content.replace("</Track>", f"</Track>\n{contents}")
    new_content = new_content.replace("\n\n", '\n')

    latitude=poiarray[0,0]
    longitude= poiarray[0,1]
    # Regular expression pattern to match the desired block
    pattern = r"(<BeginPosition>\s*)<LatitudeDegrees/>\s*<LongitudeDegrees/>\s*(</BeginPosition>)"
    # Replacement text using the variables
    replacement = fr"\g<1><LatitudeDegrees>{latitude}</LatitudeDegrees>\n          <LongitudeDegrees>{longitude}</LongitudeDegrees>\n        \g<2>"
    # Perform the substitution
    new_content2 = re.sub(pattern, replacement, new_content)

    latitude=poiarray[-1,0]
    longitude= poiarray[-1,1]
    # Regular expression pattern to match the desired block
    pattern = r"(<EndPosition>\s*)<LatitudeDegrees/>\s*<LongitudeDegrees/>\s*(</EndPosition>)"
    # Replacement text using the variables
    replacement = fr"\g<1><LatitudeDegrees>{latitude}</LatitudeDegrees>\n          <LongitudeDegrees>{longitude}</LongitudeDegrees>\n        \g<2>"
    # Perform the substitution
    new_content2 = re.sub(pattern, replacement, new_content2)

    # Variable for the new name
    new_name = basename_without_ext
    # Regular expression pattern to match the <Id> tag and its content
    pattern = r"(<CourseNameRef>\s*<Id>)(.*)(</Id>\s*</CourseNameRef>)\n"
    # Replacement text using the new variable
    replacement = fr"\g<1>{new_name}\g<3>\n"
    # Perform the substitution
    new_content2 = re.sub(pattern, replacement, new_content2)

    pattern = r"(<Name>)(.*?)(</Name>)"
    replacement = fr"\g<1>{new_name}\g<3>"
    new_content3 = re.sub(pattern, replacement, new_content2, count=1)  # count=1 ensures only the first <Name> is replaced

    # Write the updated content back to the file
    with open(output_file2, 'w') as file2:
        file2.write(new_content3)
    # Close the memory file when done
    pass

    with open(output_file2, 'r') as file:
        content3 = file.read()
    # Find all occurrences of </Track> and insert text after them
    new_content3 = content3.replace("<TotalTimeSeconds/>", f"<TotalTimeSeconds>{tti*10}</TotalTimeSeconds>\n")
    new_content3 = new_content3.replace("\n\n", '\n')
    new_content3 = new_content3.replace("<DistanceMeters/>", f"<DistanceMeters>{distf}</DistanceMeters>\n")
    new_content3 = new_content3.replace("\n\n", '\n')

    with open(output_file2, "w", encoding="utf-8") as file:
        file.write(new_content3)
memory_file.close()  # Explicitly closing the StringIO object

#GPX.studio wpt:
#'Accommodation', 'Alert', 'Anchor', 'Bank', 'Beach', 'Bike Trail', 'Binoculars', 'Bridge', 'Building',
#'Campsite', 'Car', 'Convenience Store', 'Crossing', 'Department Store', 'Exit', 'Forest', 'Fuel Station',
#'Garage', 'Ground Transportation', 'Hotel', 'House', 'Hut', 'Information', 'Park', 'Parking', 'Pharmacy',
#'Picnic Area', 'Restaurant', 'Restricted Area', 'Road', 'Scenic Area', 'Shelter', 'Shopping Center',
#'Shower', 'Summit', 'Telephone', 'Toilets', 'Tunnel', 'Water', 'Water Source'

#Line 2001, Column 0: Element '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}PointType': 
# [facet 'enumeration'] The value 'tmp' is not an element of the set 
# {'Generic', 'Summit', 'Valley', 'Water', 'Food', 'Danger', 'Left', 'Right', 'Straight', 'First Aid', 
# '4th Category', '3rd Category', '2nd Category', '1st Category', 'Hors Category', 'Sprint'}.
