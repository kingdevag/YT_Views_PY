# -*- coding: utf-8 -*-

#LIBRERIAS
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload #Miniatura

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from time import time, sleep
from config import *
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

#LIBRERIAS
#pip install google_auth_oauthlib
#pip install google-api-python-client
#pip install --upgrade google-api-python-client
#pip install --upgrade google-auth-oauthlib google-auth-httplib2
#pip install Pillow

#TEXTO
def PonerTexto():
    os.system("cls")                                                
    print("                                                         ")
    print(" ________           __                          __       ")
    print("/        |         /  |                        /  |      ")
    print("$$$$$$$$/______   _$$ |_    __    __   _______ $$ |   __ ")
    print("   $$ | /      \ / $$   |  /  |  /  | /       |$$ |  /  |")
    print("   $$ | $$$$$$  |$$$$$$/   $$ |  $$ |/$$$$$$$/ $$ |_/$$/ ")
    print("   $$ | /    $$ |  $$ | __ $$ |  $$ |$$ |      $$   $$<  ")
    print("   $$ |/$$$$$$$ |  $$ |/  |$$ \__$$ |$$ \_____ $$$$$$  \ ")
    print("   $$ |$$    $$ |  $$  $$/ $$    $$/ $$       |$$ | $$  |")
    print("   $$/  $$$$$$$/    $$$$/   $$$$$$/   $$$$$$$/ $$/   $$/  API by Google Developers <3")
    print( )

#VARIABLES PREDEFINIDAS
api_service_name = "youtube"
api_version = "v3"
visitas = "0"
categoryID = "0"
video = "holo"
vecesActualizado = 0
vecesSolicitado = 0

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    #VARIABLES CAMBIABLES
 

    #OBTENER CREDENCIALES Y API
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    #OBTENER TITULO ANTIGUO
    def ObtenerValoresOriginales():
        global video
        videoLista = youtube.videos().list(
                part="snippet,statistics",
                id=IDVideo
        )
        videoJSON = videoLista.execute() 
        video = videoJSON["items"]
        return video
        
    ObtenerValoresOriginales()

    def ObtenerTituloOriginal():
        global tituloVideo
        tituloVideo = ObtenerValoresOriginales()[0]["snippet"]["title"]
        return tituloVideo
        
    #PARA USAR PON: ObtenerTituloOriginal()

    def ObtenerDescripcionOriginal():
        global descripcionVideo
        descripcionVideo = ObtenerValoresOriginales()[0]["snippet"]["description"]
        return descripcionVideo
        
    #PARA USAR PON: ObtenerDescripcionOriginal()   

    def ObtenerEtiquetasOriginal():
        global etiquetasVideo
        etiquetasVideo = ObtenerValoresOriginales()[0]["snippet"]["tags"]
        return etiquetasVideo
        
    #PARA USAR PON: ObtenerEtiquetasOriginal()

    def CrearMiniatura(visitas):
        imagen = Image.open("miniOriginal.png")
        draw = ImageDraw.Draw(imagen)

        font = ImageFont.truetype("coolvetica.ttf", 400)
        fontVideo = ImageFont.truetype("coolvetica.ttf", 120)

        anchoFoto, altoFoto = (1366,768)

        textoArriba = "Este vídeo tiene:"
        textoAbajo = "VISITAS"
        
        anchoTextoArriba, altoTextoArriba = draw.textsize(textoArriba, font=fontVideo)
        anchoTextoVisitas, altoTextoVisitas = draw.textsize(visitas, font=font)
        anchoTextoAbajo, altoTextoAbajo = draw.textsize(textoAbajo, font=fontVideo)
        
        draw.text(((anchoFoto-anchoTextoArriba)/2,(altoFoto-altoTextoArriba)/2-210),textoArriba,(0,0,0),font=fontVideo)
        draw.text(((anchoFoto-anchoTextoVisitas)/2,(altoFoto-altoTextoVisitas-107)/2),visitas,(255,0,0),font=font) #107 = 400(tamano letra) *32(texto sin baseline superior a tamano 120) / 120
        draw.text(((anchoFoto-anchoTextoAbajo)/2,(altoFoto-altoTextoAbajo)/2+220),textoAbajo,(0,0,0),font=fontVideo)
        
        imagen.save('miniFinal.png')
        
    #CREAR TITULO
    def CrearYActualizarTitulo():

        global vecesActualizado
        global vecesSolicitado

        PonerTexto()

        #OBTENER DATOS   
        
        vecesSolicitado = vecesSolicitado +1
        
        global categoryID
        global visitas
        videoLista = youtube.videos().list(
                part="snippet,statistics",
                id=IDVideo
        )
        videoJSON = videoLista.execute() 
        video = videoJSON["items"]

        categoryID = video[0]["snippet"]["categoryId"]
        visitas = video[0]["statistics"]["viewCount"]

        videoTituloANTES = video[0]["snippet"]["title"]

        #CREACION NUEVO TITULO
        nuevoTitulo = tituloVideo + " VISITAS: "+visitas
        
        print("Titulo antiguo: "+ tituloVideo)
        print("Visitas: "+visitas)
        #ACTUALIZAR DATOS
        #AL ACTUALIZAR DATOS, TODOS LOS VALORES QUE NO ESTEN PUESTOS DESAPARECERÁN DEL VIDEO ORIGINAL(descripcion, etiquetas...)
        if videoTituloANTES != nuevoTitulo:
            
            vecesActualizado = vecesActualizado + 1

            CrearMiniatura(visitas)
            request = youtube.videos().update(
                part="snippet",
                body={
                  "id": IDVideo,
                  "snippet":{
                    "title":nuevoTitulo,
                    "description":ObtenerDescripcionOriginal(),
                    "tags":ObtenerEtiquetasOriginal(),
                    "categoryId":categoryID
                  }
                }
                
        
            ).execute()
            
            request = youtube.thumbnails().set(
                 videoId=IDVideo,
                 
                 media_body=MediaFileUpload("miniFinal.png")
            ).execute()
            
            
        
            print("Nuevo titulo: "+ nuevoTitulo)
            print("Miniatura actualizada con: "+ str(visitas))

        print("Veces datos solicitados: "+ str(vecesSolicitado))
        print("Veces datos actualizados: "+ str(vecesActualizado))
        
    while True:
        CrearYActualizarTitulo()      
        sleep(tiempoActualizacion - time() % tiempoActualizacion)
       
        

if __name__ == "__main__":
    main()