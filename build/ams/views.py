from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from PIL import Image,ImageFont,ImageDraw
import io
from io import BytesIO

import time
import face_recognition
import numpy as np
from ams.models import Attendance,e2csecse2
from django.db import connections
from datetime import datetime
import os
from django.template import loader
# g=set()
# client=str()
# ver=int()
# it=int()
@csrf_exempt
def home(request):
    template=loader.get_template('index.html')
    return HttpResponse(template.render())

@csrf_exempt
def identify(request):
    global ver
    if request.method == 'POST':
        data=json.loads(request.body)
        image_data =data["image_data"]

        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            np=Image.open(BytesIO(image_data))

            IMAGE =np.rotate(90, expand=True)
            # IMAGE.show()
            with BytesIO() as output:
                IMAGE.save(output, format='PNG')
                image_bytes = output.getvalue()
            IMAGE = BytesIO(image_bytes)

            
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5
            # ROOT_DIR = '/content/drive/MyDrive/AMS_MINI_PROJECT'
            FONT = ImageFont.truetype('./arial.ttf', 16)
            # IMAGE="d.jpg"

            image = face_recognition.load_image_file(IMAGE)
            if max(image.shape) > 1600:
                pil_img = Image.fromarray(image)
                pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                image = np.array(pil_img)
            else:
                print("some error")
            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            md=data["data"]
            strg=md["class"]+md["branch"]+md["section"]+".json"
            
            with open("./models/"+strg,"r") as f:
                global total
                dat=json.load(f)
                known_faces=dat["known_faces"]
                
                total=set(known_faces.keys())
            findings=set()
            for face_encoding, face_location in zip(encodings, locations):
                match=None
                for i in known_faces:
                    
                    results = face_recognition.compare_faces(known_faces[i], face_encoding, TOLERANCE)
                    per=0
                    if (len(results)!=0):
                        per=results.count(True)/len(results)
                    top, right, bottom, left = face_location
                    if (per>=0.5):      
                        draw.rectangle(((left, top), (right, bottom)), outline='green', width=2)
                        draw.text((left+6, top-20), i, font=FONT, fill='green')
                        
                        findings.add(i)
                        match=True
                        break
                if (match==None):
                    draw.rectangle(((left, top), (right, bottom)), outline='red', width=2)
                    draw.text((left+6, top-20), "unknown", font=FONT, fill='red')
          
            
            idb=findings
            
            date=datetime.now().strftime("%Y%m%d")
            col=""
            q=""
            q2=""
            # print(len(findings),"",len(total),"",len(g))
            
            if (len(idb)>=1):
                for i in idb:
                    print(i)
                    col+=f"{i},"
                    q+=f"'1',"
                    q2+=f"{i}='1',"
                del draw
                print("hello",col,"\n",q,"\n",q2)
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG')
                reply = base64.b64encode(buffer.getvalue())
                cur=connections["seconddb"].cursor()
                
                table=md["class"]+md["branch"]+md["section"]
                cur.execute(f"select date from {table} where date={date}")
                if(len(cur.fetchall())==0):
                    print(f"insert into {table}('date,'{col[0:-1]}) values('{date}','{q[0:-1]}) ")
                    dateInsertion(table,date)
                    cur.execute(f"insert into {table}(date,{col[0:-1]}) values('{date}',{q[0:-1]}) ")
                    Attendance(table,idb,date)
                else:
                    print(f"update {table} set {q2[0:-1]} where date='{date}' ")
                    cur.execute(f"update {table} set {q2[0:-1]} where date='{date}'")
                    # print(table)
                    Attendance(table,idb,date)
                    print("hi")
                return JsonResponse({"image":"data:image/jpeg;base64,"+reply.decode("utf-8"),"findings":list(idb)})
            else:
                return JsonResponse({"image":0})

        else:
            return JsonResponse({"prompt":"not a correct image"})
   
@csrf_exempt
def Login(request):
    global client
    from .models import Credentials
    if request.method=='POST':
        data=json.loads(request.body)
        print(data)
        cur=connections['seconddb'].cursor()
        cur.execute(f"select * from credentials where username='{data['username']}' and password={data['password']}")
        check=cur.fetchall()
        cur.close()
        print(len(check))
        if(len(check)==1):
            client=data["username"]
            print("hi")
            return JsonResponse({"Login":1})
        else:
            return JsonResponse({"Login":0})
        
    else:
        return JsonResponse({"Login":"failure"})
@csrf_exempt
def Verify(req):

  try:
    if req.method == 'POST':
        data=json.loads(req.body)
        # print(len(data))
        
        image_data =data["image_data"]
        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            IMAGE =io.BytesIO(image_data)
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5 
            
        
            image = face_recognition.load_image_file(IMAGE)
            locations = face_recognition.face_locations(image, model=MODEL)
            encodings = face_recognition.face_encodings(image, locations)
            
            # print(len(encodings))
         
            with open("./faculty.json","r") as f:
                
                data=json.load(f)
                known_faces=data["known_faces"]
            for face_encoding, face_location in zip(encodings, locations):
                match=None
                print(client)
                results = face_recognition.compare_faces(known_faces[client], face_encoding, TOLERANCE)
                per=0
                
                if (len(results)!=0):
                    per=results.count(True)/len(results)
                else:
                    return JsonResponse({"verification":0})

                if (per>=0.5):
                    ver=1
                    return JsonResponse({"verification":1})
                else:
                    
                    return JsonResponse({"verification":0})
            
            

                # return JsonResponse({"image":"data:image/jpeg;base64,"+reply.decode("utf-8"),"findings":findings})
        else:
            return JsonResponse({"verification":0})
    else:
         return JsonResponse({"verification":0})
  except Exception as e:
    return JsonResponse({"verification":0})

@csrf_exempt
def newreg(req):
    try:
    # global ver
        if req.method == 'POST':
            data=json.loads(req.body)
            print(len(data))
            
            image_data =data["image_data"]
            if image_data:
                # decode the base64 encoded image data
                image_data = base64.b64decode(image_data.split(',')[1])
                IMAGE =io.BytesIO(image_data)
                MODEL = 'hog'  # 'hog' or 'cnn'
                #constants declaration
                TOLERANCE = 0.5
                
                md=data["data"]
                ID=md["user"].upper()
                strg=md["class"]+md["branch"]+md["section"]+".json"
                print(strg)
                with open("./models/"+strg,"r+") as x:
                    
                    
                    model=json.load(x)
                    print("heee")
                    it=int(data["tt"])
                    print(it)
                    image = face_recognition.load_image_file(IMAGE)

                    if (it==0):
                        print("test2")
                        known=list(model["known_faces"].keys())
                        
                        if(md["user"]) not in known:
                            print("hellow")
                            size = os.path.getsize("./models/"+strg)
                            x.seek(size-2,0) 
                            if max(image.shape) > 1600:
                                pil_img = Image.fromarray(image)
                                pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                                image = np.array(pil_img)
                            encoding = face_recognition.face_encodings(image)
                            if(len(encoding)==1):
                                dat='"'+ID+'"'+":"+str([encoding[0].tolist()])
                                t=","+dat+"}}"
                                table=md["class"]+md["branch"]+md["section"]
                                excelnewreg(table,md["user"])
                                
                                
                                os.mkdir(os.path.join("pictures",md["class"],md["branch"],md["section"],md["user"]))
                                now = str(datetime.now()).replace(':', '_')
                                Image.fromarray(image).save(os.path.join("pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                                x.write(t)
                                cur=connections["seconddb"].cursor()
                                table=md["class"]+md["branch"]+md["section"]
                                cur.execute(f"alter table {table} add column {md['user']} int(1) default 0 ")
                                
                                it+=1
                                return JsonResponse({"message":1})
                            else:
                                return JsonResponse({"message":"images>1/0 found"})
                        else:
                            return JsonResponse({"message":"already exists"})
                    elif(it<5):
                        if max(image.shape) > 1600:
                            pil_img = Image.fromarray(image)
                            pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                            image = np.array(pil_img)
                        encoding = face_recognition.face_encodings(image)
                        if(len(encoding)==1):
                            model["known_faces"][ID].append(encoding[0].tolist())
                            x.seek(0,0)
                            json.dump(model,x)
                            now = str(datetime.now()).replace(':', '_')
                            Image.fromarray(image).save(os.path.join("./pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                            it+=1
                            return JsonResponse({"message":1,"it":it})                    
                        else:
                            return JsonResponse({"message":"images>1/0 found","it":it})
                    elif(it==5):
                        return JsonResponse({"message":1,"it":5})
                    else:
                        return JsonResponse({"message":1,"it":6})    
            else:
                return JsonResponse({"message":"no face found"})
    except Exception as e:
        print(e)
        return JsonResponse({"message":"some error"})
@csrf_exempt
def update(req):
   if req.method == 'POST':
        data=json.loads(req.body)
        print(len(data))
        
        image_data =data["image_data"]
        if image_data:
            # decode the base64 encoded image data
            image_data = base64.b64decode(image_data.split(',')[1])
            IMAGE =io.BytesIO(image_data)
            MODEL = 'hog'  # 'hog' or 'cnn'
            #constants declaration
            TOLERANCE = 0.5
            
            md=data["data"]
            ID=md["user"]
            strg=md["class"]+md["branch"]+md["section"]+".json"
            with open("./models/"+strg,"r+") as x:
                model=json.load(x)
                image = face_recognition.load_image_file(IMAGE)
                known=list(model["known_faces"].keys())
                if(ID) in known:
                    if max(image.shape) > 1600:
                        pil_img = Image.fromarray(image)
                        pil_img.thumbnail((1600, 1600), Image.LANCZOS)
                        image = np.array(pil_img)
                    encoding = face_recognition.face_encodings(image)
                    if(len(encoding)==1):
                        model["known_faces"][ID].append(encoding[0].tolist())
                        x.seek(0,0)
                        json.dump(model,x)
                        now = str(datetime.now()).replace(':', '_')
                        Image.fromarray(image).save(os.path.join("./pictures",md["class"],md["branch"],md["section"],md["user"],now)+".png")
                        return JsonResponse({"message":1})                    
                    else:
                        return JsonResponse({"message":"images>1/0 found"})
                else:
                    return JsonResponse({"message":"Try new Registrations"})
        else:
            return JsonResponse({"message":"no face found"})


def excelnewreg(worksheet_name,user):
        print("test1")
        import datetime
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        SERVICE_ACCOUNT_FILE = './service.json'
        
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        service_sheets = build('sheets', 'v4', credentials=credentials)
        GOOGLE_SHEETS_ID = '1TkXFVCGrrMMkLE1y5z4fMJ9JkOYT7PRRYThYN_imBfY'
        

        cell_ranges = [
            'A1:A',
            'A1:1'
        ]

        ranges = [worksheet_name + '!' + cell_range for cell_range in cell_ranges]

        response = service_sheets.spreadsheets().values().batchGet(
            spreadsheetId=GOOGLE_SHEETS_ID,
            ranges=ranges
        ).execute()
        print("hello mawsboro")
        dates=response["valueRanges"][0]["values"][1:]
        ids=response["valueRanges"][1]["values"][0]
        

        columns=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE","AF",
        "AG","AH","AI","AJ","AK","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AV","AW","AX","AY","AZ","BA"]
        ranges=columns[len(ids)]+str(1)
        body1={
        'values':[[user]]
        }        
        range = service_sheets.spreadsheets().values().update(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range=worksheet_name + '!' + ranges,
            valueInputOption='RAW',
            body=body1
        ).execute()
def Attendance(worksheet_name,users,today):
    import datetime
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SERVICE_ACCOUNT_FILE = './service.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    service_sheets = build('sheets', 'v4', credentials=credentials)

    GOOGLE_SHEETS_ID = '1TkXFVCGrrMMkLE1y5z4fMJ9JkOYT7PRRYThYN_imBfY'

    cell_ranges = [
        'A1:A',
        'B1:1'
    ]
    print(worksheet_name)
    ranges = [worksheet_name + '!' + cell_range for cell_range in cell_ranges]

    response = service_sheets.spreadsheets().values().batchGet(
        spreadsheetId=GOOGLE_SHEETS_ID,
        ranges=ranges
    ).execute()
    dates=response["valueRanges"][0]["values"][1:]
    ids=response["valueRanges"][1]["values"][0]
    
    date=[today]
    value_range={"data":[],'valueInputOption': 'RAW'}
    for i in users:
        idi=ids.index(i)+1
        ddi=dates.index(date)+2
        columns=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE","AF"
        "AG","AH","AI","AJ","AK","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AV","AW","AX","AY","AZ","BA"]
        value_range["data"].append({'range':worksheet_name+"!"+columns[idi]+str(ddi),'values':[['1']]})
    response = service_sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=GOOGLE_SHEETS_ID,
        body=value_range,
    ).execute()
    print(response) 
def dateInsertion(worksheet_name,date):
    import datetime
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SERVICE_ACCOUNT_FILE = './service.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    service_sheets = build('sheets', 'v4', credentials=credentials)

    GOOGLE_SHEETS_ID = '1TkXFVCGrrMMkLE1y5z4fMJ9JkOYT7PRRYThYN_imBfY'
    

    cell_ranges = [
        'A1:A',
        'B1:1'
    ]

    ranges = [worksheet_name + '!' + cell_range for cell_range in cell_ranges]

    response = service_sheets.spreadsheets().values().batchGet(
        spreadsheetId=GOOGLE_SHEETS_ID,
        ranges=ranges
    ).execute()
    dates=response["valueRanges"][0]["values"][1:]
    ids=response["valueRanges"][1]["values"][0]
    ranges="A"+str(len(dates)+2)
    
    body1={
        'values':[[date]]
    }
    range = service_sheets.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=worksheet_name + '!' + ranges,
        valueInputOption='RAW',
        body=body1
    ).execute()