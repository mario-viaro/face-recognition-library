import os
import argparse
import json
import face_recognition


def camera_img_issue(image_path, face_found, similar_faces, multi_faces):
    camera_report_text = "\n \t {\"image\": {"
    camera_report_text += "\n \t \t \"fileName\": \"" + image_path + "\","
    
    # Face found
    if similar_faces:
        camera_report_text += "\n \t \t \"faceFound\": true,"
    elif face_found:
	    camera_report_text += "\n \t \t \"faceFound\": true,"
    else:
	    camera_report_text += "\n \t \t \"faceFound\": false,"

    # Similar faces
    if similar_faces:
        camera_report_text += "\n \t \t \"similarFaces\": true,"
    else:
        camera_report_text += "\n \t \t \"similarFaces\": false,"

    #Multiple faces
    if multi_faces:
        camera_report_text += "\n \t \t \"moreFacesDetected\": true"
    else:
        camera_report_text += "\n \t \t \"moreFacesDetected\": false"

    camera_report_text += "\n \t }"
    camera_report_text += "\n \t },"

    return camera_report_text

def raise_error(path, folder):
    #os.system('python ' + remove_script_path + remove_script + " " + path + " " + folder)
    print("{\n \t \"outputMessage\": \"error\" \n}")

def raise_no_images():
    print("{\n \t \"outputMessage\": \"no images\" \n}")

def raise_succeed():
    print("{\n \t \"outputMessage\": \"succeed\" \n}")

def identify_camera_images(single_folder, objects, detected_faces_person, folder):
    camera_list = []

    #Order the pictures
    full_camera_report = ' '
    for obj in objects:
        if "camera_" in obj:
            camera_list.append(single_folder + "/" + obj)

    camera_list = sorted(camera_list)

    for pic in camera_list:
        issue_found = False
        issue_face_found = False
        issue_similar = False
        issue_multi_faces = False
        
        try:
            face_pic_stream = face_recognition.load_image_file(pic)
            face_pic_detected =  face_recognition.face_encodings(face_pic_stream)[0]
            issue_face_found = True

            similar_faces = face_recognition.compare_faces([detected_faces_person], face_pic_detected)
            
            if(similar_faces[0]):
                issue_similar = True
            else:
                issue_found = True

            faces = face_recognition.face_locations(face_pic_stream, number_of_times_to_upsample=1, model='hog')
            if(len(faces) > 1):
                issue_multi_faces = True
                issue_found = True
        except:
            issue_found = True
        
        if(issue_found):
            full_camera_report += camera_img_issue(pic, issue_face_found, issue_similar, issue_multi_faces)

    return full_camera_report

def identify_face(path, folder):
    bucket_folders=[]

    # output values
    output_no_images = False
    output_process_error = False
    output_succeed = False
    
    bucket_folders.append(folder)

# Face recognition
    for folder_name in bucket_folders:
        single_folder = path + folder_name
        second_image_face_id = None
        
        objects = os.listdir(single_folder)

        if len(objects) < 1:
            report_text = "No images on the folder " + single_folder[:1]
            output_no_images = True

        else:
            report_text = ""
            document_image_found = False
            person_image_found = False
            detected_faces_doc_bool = False
            detected_faces_person_bool = False
            document_pic_name_text = ""
            person_pic_name_text = ""
            
            for obj in objects:
                if ('document_' in obj) or ('verification_document' in obj): # Find the first image and detect the face
                    document_image_found = True
                    document_pic_name = single_folder + "/" + obj
                    document_pic_name_text = folder + "/" + obj
                elif ('person_' in obj) or ('verification_person' in obj): # Find the second image and detect the face
                    person_image_found = True
                    person_pic_name = single_folder + "/" + obj
                    person_pic_name_text = folder + "/" + obj

            
            #Validate Person Image
            second_image_face_ids = None
            if person_image_found:
                report_text += "\"personImage\": {"
                report_text += "\n \t \"fileName\": \"" + person_pic_name_text + "\","
                try:
                    person_img_stream = face_recognition.load_image_file(person_pic_name)
                    detected_faces_person =  face_recognition.face_encodings(person_img_stream)[0]

                    report_text += "\n \t \"faceDetected\": true,"

                    detected_faces_person_bool = True

                    faces = face_recognition.face_locations(person_img_stream, number_of_times_to_upsample=1, model='hog')
                    
                    if (len(faces) > 1):
                        report_text += "\n \t \"moreFacesDetected\": true"
                    else:
                        report_text += "\n \t \"moreFacesDetected\": false"

                    report_text = report_text + "\n },"
                    output_succeed = True

                except IndexError as e:
                    output_process_error = True
                    report_text += "\n \t \"faceDetected\": false"
                    report_text = report_text + "\n },"
            else:
                report_text +="\n \"personImage\": {"
                report_text = report_text + "\n },"


            #Validate Document Image
            if document_image_found:
                report_text +="\n \"documentImage\": {"
                report_text += "\n \t \"fileName\": \"" + document_pic_name_text + "\","
                try:
                    
                    document_img_stream = face_recognition.load_image_file(document_pic_name)
                    detected_faces_doc =  face_recognition.face_encodings(document_img_stream)[0]
                    
                    detected_faces_doc_bool = True

                    report_text +="\n \t \"faceDetected\": true"

                    faces = face_recognition.face_locations(document_img_stream, number_of_times_to_upsample=1, model='hog')

                    report_text = report_text + "\n },"

                except:
                    report_text += "\n \t \"faceDetected\": false"
                    report_text = report_text + "\n },"
                
            else:
                report_text +="{ \n \"documentImage\": {"
                report_text = report_text + "\n },"

            #Validate Person Image VS Document Image
            report_text += "\n \"documentAndPersonValidation\": {"
            if detected_faces_person_bool and detected_faces_doc_bool:
                report_text += "\n \t \"facesDetectedOnBothImages\": true,"

                try:
                    similar_faces = face_recognition.compare_faces([detected_faces_person], detected_faces_doc)
                    
                    if similar_faces[0] == True:
                        report_text += "\n \t \"similarFaces\": true"
                    else:
                        report_text += "\n \t \"similarFaces\": false"
                        

                except:
                    output_process_error = False

            report_text = report_text + "\n },"

            #For all the other picturs look validate
            report_text += "\n \"cameraImages\": ["
            
            if(detected_faces_person_bool):
                report_text += identify_camera_images(single_folder, objects, detected_faces_person, folder)[:-1]

            report_text = report_text + "\n ]"

            report_text = "{ \n " + report_text + "\n }"

            #Transform report text to json
            arr_noface_issue = []
            arr_normal_issue = []
            json_report = json.loads(report_text)
            
            for img_element in json_report['cameraImages']:
                    if img_element['image']['faceFound'] == False:
                            arr_noface_issue.append(img_element)
                    else:
                            arr_normal_issue.append(img_element)

            if len(arr_noface_issue) > 8:
                arr_interval = []
                pos_interval = int(round(1.0 * len(arr_noface_issue) / 8))

                for x in range(0, len(arr_noface_issue) - 1, pos_interval):
                        arr_interval.append(arr_noface_issue[x])

                json_report['cameraImages'] = arr_normal_issue + arr_interval
                json_str = json.dumps(json_report)
                report_text = json_str
            
            print("$$$$$"+report_text+"$$$$$")

    # Output message
    if output_no_images:
        raise_no_images()
    elif output_process_error:
        raise_error(path, folder)
    elif output_succeed:
        raise_succeed()
    
    

def main(path, folder):
    identify_face(path, folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detects faces in the given folder.')
    parser.add_argument('path', help='Path')
    parser.add_argument('folder', help='Folder')
    args = parser.parse_args()
    main(args.path, args.folder)
