# A mi hermano Enrique y a su grupo de senderismo Ayuco.
# Por la recuperación de los montes de Gran Canaria.
# Para que no vuelva a pasar nunca mas.

import requests
from bs4 import BeautifulSoup
import os
import time
import datetime
import csv



class SpeciesScraper():
    
    # "CONSTRUCTOR" web-scraper. Inicializamos cabecera de las peticiones, pagina
    # de partida, carpetas y estructura de datos necesarias.
    # Manejo excepciones al crear la carpeta
    
    def __init__(self):
        
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3","Accept-Encoding": "gzip, deflate, br", "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,gl;q=0.7"}
        
        self.starturl = "http://www.arbolappcanarias.es/especies-nombre-cientifico"
        
        self.imagfolder = r'../images'
        self.datafolder = r'../data'
        
        self.species_data = []
        self.not_recovered_lnk = [] 
        
        # crear carpeta imagenes
        try:
            
            if not os.path.exists(self.imagfolder):
                os.makedirs(self.imagfolder)
            
            else:
                # Advertir que la carpeta de imagenes ha de estar vacia antes de hacer
                # un nuevo "escaneado"
                print("¡¡ ATENCION !! Debe borrar (o guardar en otra ubicación) el contenido de la carpeta 'images'. La carpeta debe estar vacia.")
        
        # manejo excepciones al crear carpeta                
        except OSError as e:
            
            print('Error al crear la carpeta de imagenes')
            print("Descripcion:\n {descr}".format(descr=e))
        
        
        
    # DESCARGA PAGINA WEB: argumentos 'url' de la pagina, opcionales numero de reintentos
    # y retardo entre intentos. Manejo de las posibles respuestas y excepciones .        
        
    def __download_html(self,url,num_retries=5,retry_delay=5):
        
        try:
            
            # peticion
            resp = requests.get(url, headers=self.headers)
            
            # respuesta con exito, descarga de la pagina completada
            if resp.status_code == 200:
                
                print("{tiempo}: solicitud a {url} completada con exito".format(url=url,tiempo=datetime.datetime.now()))
                return resp.content
            
            # respuesta: error del cliente,por ejemplo pagina no encontrada (no se encuentra
            # en el servidor la pagina solicitada). En estos casos no se hacen nuevas peticiones.
            elif 400 <= resp.status_code < 500:
                
                print("{tiempo}: Error en solicitud a {url}, cod: {cod}".format(url=url,tiempo=datetime.datetime.now(),cod=resp.status_code))
                return None
            
            
            # respuesta: error del servidor, por ejemplo errores internos, falta de disponibilidad
            # temporal. Repetir peticiones con retardos cada vez mayores. Numero de reintentos y
            # retardos establecido en la llamada al metodo o en ausencia valores por defecto
            elif  500 <= resp.status_code < 600:
                
                if num_retries >0:
                    
                    # no se ha alcanzado el limite, quedan reintentos por hacer
                    print("{tiempo}: Error en solicitud a {url}, cod: {cod}, repitiendo solicitud".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
                    
                    # retardo entre intentos
                    time.sleep(retry_delay)
                    
                    return self.__download_html(url, num_retries - 1,retry_delay*1.5)
            
                else:
                    
                    # agotado el numero de reintentos sin repuesta. Devolvemos valor "None"
                    # para notificarlo al metodo que ha realizado la llamada.
                    print("{tiempo}: Error en solicitud a {url}, cod: {cod}, no hay respuesta".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
                    return None

            
        # Excepcion "Timeout". Si no hay respuesta del servidor realizamos reintentos con retardos
        # cada vez mayores.            
        except requests.exceptions.Timeout:
            
            print("{tiempo}: {url}, servidor no responde, cod: {cod}, repitiendo solicitud".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
            time.sleep(retry_delay)
            return self.__download_html(url, num_retries - 1,retry_delay*1.5)
    
        # Manejo de otras posibles excepciones de la peticion, presentar por pantalla mensaje   
        except requests.exceptions.RequestException as e:
            
            print("{tiempo}: {url} Error en la descarga.\n".format(url=url, tiempo=datetime.datetime.now()))
            print("Descripcion:\n {descr}".format(descr=e))
            return None
        
   

    # DESCARGA IMAGEN DE LA WEB: argumentos 'url' de la imagen, ruta donde guardarla, opcionales
    # numero de reintentos y retardo entre intentos. Manejo de las posibles respuestas y excepciones .                
    def __download_imag(self,url,path,num_retries=5,retry_delay=1):
              
        try:
            
            # peticion
            resp = requests.get(url, headers=self.headers, stream=True)
            
            # respuesta con exito, descarga de la imagen completada
            if resp.status_code == 200:
                
                # descarga de la imagen dividida en fragmentos: [resp.iter_content(chunk_size = 1024]
                with open(path, "wb") as file:
                    for chunk in resp.iter_content(chunk_size = 1024):
                        if chunk:
                            file.write(chunk)
                    
                print("{tiempo}: solicitud a {url} completada con exito".format(url=url,tiempo=datetime.datetime.now()))
    
            
            # respuesta: error del cliente, por ejemplo pagina no encontrada (no se encuentra
            # en el servidor la pagina solicitada). En estos casos no se hacen nuevas peticiones.
            elif 400 <= resp.status_code < 500:
                
                print("{tiempo}: Error en solicitud a {url}, cod: {cod}".format(url=url,tiempo=datetime.datetime.now(),                                                                             cod=resp.status_code))


            # respuesta: error del servidor, por ejemplo errores internos, falta de disponibilidad
            # temporal. Repetir peticiones con retardos cada vez mayores. Numero de reintentos y
            # retardos establecido en la llamada al metodo o en ausencia valores por defecto            
            elif  500 <= resp.status_code < 600:
                
                # no se ha alcanzado el limite, quedan reintentos por hacer
                if num_retries >0:
                    print("{tiempo}: Error en solicitud a {url}, cod: {cod}, repitiendo solicitud".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
                    time.sleep(retry_delay)
                    return self.__download_imag(url, path, num_retries - 1, retry_delay*1.3)
                
                # agotado el numero de reintentos sin repuesta. Devolvemos valor "None"
                # para notificarlo al metodo que ha realizado la llamada.
                else:
                    print("{tiempo}: Error en solicitud a {url}, cod: {cod}, no hay respuesta".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
                    return None
            

        # Excepcion "Timeout". Si no hay respuesta del servidor realizamos reintentos con retardos
        # cada vez mayores.            
        except requests.exceptions.Timeout:
        
            print("{tiempo}: {url}, servidor no responde, cod: {cod}, repitiendo solicitud".format(url=url, tiempo=datetime.datetime.now(), cod=resp.status_code))
            time.sleep(retry_delay)
            return self.__download_imag(url, path, num_retries - 1, retry_delay*1.3)
    

        # Manejo de otras posibles excepciones de la peticion, presentar por pantalla mensaje    
        except requests.exceptions.RequestException as e:
            
            print("{tiempo}: {url} Error en la descarga.\n".format(url=url, tiempo=datetime.datetime.now()))
            print("Descripcion:\n {descr}".format(descr=e))
            
        # Manejo excepciones al guardar imagenes. Presentar mensaje por pantalla            
        except OSError as e:
            
            print('Error al almacenar las imagenes en disco.')
            print("Descripcion:\n {descr}".format(descr=e))
            
    
    
    
    # METODO ENCONTRAR ISLAS: a partir de texto obtenido de la sección "DISTRIBUCIÓN" de la
    # pagina web de la especie, encuentra ocurrencias de las islas. Si no encuentra ninguna es
    # que la especie se localiza en todo el archipielago. Devuelve cadena con las islas separada por comas.
    def __find_islands(self,text):
        
        ISLANDS = set(['GRAN CANARIA','LANZAROTE','FUERTEVENTURA','TENERIFE','LA PALMA','GOMERA','HIERRO'])
        
        # inicializamos salida
        islands_list = []
        
        # busqueda en el texto de cada una de las islas
        for island in ISLANDS:
            
            # encontrada isla, añadimos a la salida
            if text.upper().find(island) != -1:
                islands_list.append(island)
        
        # si no encontramos niguna isla, es todo el archipielago
        if len(islands_list)==0:
            islands_list = list(ISLANDS)
            
        return ','.join(islands_list)

    
    
    # METODO OBTENER DATOS DE LA ESPECIE: a partir del codigo html de la web de la especie obtiene
    # los datos a recuperar, por orden, nombre cientifico, nombre comun, si es o no autoctona, idem
    # con naturalizada, idem con invasora. Devuelve lista con esos datos.
    def __get_data_specie(self,html):
         
        # datos a partir de su localizacion en el codigo html de la web
        scient_name = html.find("div", class_="sixcol last").h1.text
        common_name = html.find("div", class_="sixcol last").h2.text
        bool_autoct = html.find("div", class_="sixcol last").h3.text[:2].lower() != 'no'
        
        # de la seccion "DISTRIBUCION" obtenemos resto de los datos.
        tag_distribucion = html.find("h4", text="DISTRIBUCIÓN").find_next("div", class_="especie-texto")
        
        # inicializamos a "False" las variables booleanas.
        bool_naturaliz = False
        bool_invader = False
        
        # en el codigo html se encuentran etiquetas para mostrar significado de las palabras
        # ("span" con class='glosario'). Detectamos las correspondientes al termino
        # "naturalizado" ('id'='56') y al termino "invasor" ('id'='42')
        if tag_distribucion.find("span",attrs={'id':'56'},class_='glosario'):
            bool_naturaliz = True
            
        if tag_distribucion.find("span",attrs={'id':'42'},class_='glosario'):
            bool_invader = True
        
        # para la localizacion en el archipielago de la especie llamamos al metodo 
        # ENCONTRAR ISLAS pasandole el texto de la seccion "Distribucion". Nos devuelve lista
        # con las islas.           
        localiz = self.__find_islands(tag_distribucion.get_text())
        
        # devolvemos lista con los datos recopilados de la especie
        return [scient_name,common_name,bool_autoct,bool_naturaliz,bool_invader,localiz]
    
    
    
    # METODO OBTENER IMAGENES DE LA ESPECIE: a partir del codigo html de la web de la especie
    # obtenemos sus imagenes que se guardan en una carpeta con el nombre de la especie, dentro
    # de la carpeta 'images'
    def __get_imag_specie(self,html):
        
        try:
            
            # obtener nombre de la especie, sustituir posibles espacios                        
            spec_name = html.find("div", class_="sixcol last").h1.text.replace(" ","_")
        
            # pasos necesarios para crear la carpeta de la especie en su ubicacion correcta       
            os.chdir(self.imagfolder)
            path = "./{}".format(spec_name)
        
            # si no existe la carpeta la crea, si existe presenta mensaje por pantalla y sale del metodo para evitar
            # errores y/o sobreescrituras         
            if not os.path.exists(path):
                os.makedirs(path)            
            else:
                print("¡¡ ATENCION !! La carpeta de la especie '{}' ya existe.\n Se debe borrar (o cambiar a otra ubicación) antes de iniciar. La carpeta 'images' debe estar vacia.".format(spec_name))
                return None
            
            # por cada imagen encontrada recuperamos el nombre del archivo con el que formamos ruta donde
            # guardar imagen (path_img), llamamos al metodo DESCARGAR IMAGEN con url y dicha ruta, y finalmente
            # introducimos retardo entre descargas de imagenes.                
            for imag_tag in html.find_all("a", rel="galeria"):
                path_img = os.path.join(path, imag_tag['href'].split("/")[-1])
                self.__download_imag(imag_tag['href'],path_img)
                time.sleep(0.3)
            
        
        # manejo excepciones al crear carpeta            
        except OSError as e:
            
            print('Error al crear la carpeta de especie')
            print("Descripcion:\n {descr}".format(descr=e))
            
            
     
    
    # METODO 'SCRAPE': metodo que inicia el propio 'escaneo' de la web partiendo de la determinada como atributo de la clase
    # ('starturl': "http://www.arbolappcanarias.es/especies-nombre-cientifico"). Localiza los enlaces de las distintas especies 
    # y realiza las llamadas necesarias a los otros metodos de la clase para finalmente recuperar la informacion de cada especie.
    # Los datos se  guardan en el atributo ('species_data') de la clase y las imagenes en la carpeta para cada especie dentro
    # de la carpeta 'images'
    def scrape(self,delay_btw_pages=4):
        
        # descarga pagina principal ('starturl')
        content_start = self.__download_html(self.starturl)

        # si no se consigue descargar la pagina principal salimos del metodo. El mensaje pertinente por pantalla lo habra
        # realizado el metodo descargar pagina en la linea anterior.    
        if content_start is None:
            return None

        # llamada a BeautifulSoup, crea objeto del mismo nombre con la pagina inicial
        html_start = BeautifulSoup(content_start)

        
        # para cada enlace a cada una de las especies (localizadas por [html_start.find_all("a", class_="box-especie")])
        for specie_tag in html_start.find_all("a", class_="box-especie"):

            # retardo descarga entre paginas
            time.sleep(delay_btw_pages)

            # descarga de la pagina de la especie        
            content_specie = self.__download_html(specie_tag['href'])

            # si la descarga de la pagina de la especie no se ha podido realizar, almacenamos su enlace (link) en la lista
            # atributo de la clase 'not_recovered_lnk', y continuamos con el resto de las especies
            if content_specie is None:
                self.not_recovered_lnk.append(specie_tag['href'])
                continue
            
            # llamada a BeautifulSoup, crea objeto del mismo nombre con la pagina de la especie            
            html_specie = BeautifulSoup(content_specie)
            
            # llamada a los metodos de la clase para obtener los datos y las imagenes de la especie. Los datos se almacenan
            # en el atributo 'species_data'. Las imagenes las guarda el propio metodo (en carpeta con el nombre de la especie,
            # dentro de la carpeta 'images')
            self.species_data.append(self.__get_data_specie(html_specie))
            self.__get_imag_specie(html_specie)
            
            
        # una vez recorridas todas las especies, se muestra por pantalla mensaje resumen del 'escaneo'.            
        print('RESUMEN:\n','Especies recopiladas: {}'.format(len(self.species_data)))
        print('No se recuperaron {}'.format(len(self.not_recovered_lnk)))
        

        
        
    # METODO CREAR ARCHIVO CSV CON LOS DATOS:  a partir de los datos de las especies almacenados en el atributo 'species_data'
    # crea un archivo 'csv' con esos datos. El archivo se almacena en la ubicacion dada por el atributo 'datafolder'        
    def create_csv(self):
                
        try:
            
            # si no existe la carpeta 'data' la crea. Si existiera y hubiera ya un archivo 'csv' con los datos se decide no
            # hacer ninguna acción adicional, el archivo se reescribiria.
            if not os.path.exists(self.datafolder):
                os.makedirs(self.datafolder)
                
            # dada su ubicacion creamos el archivo de datos (modo escritura)
            with open(os.path.join(self.datafolder,'species.csv'), "w", newline='') as file:
                
                # objeto 'writer' de la libreria 'csv', para escribir acorde al formato 'csv'
                writer = csv.writer(file)
                
                # para cada especie almacenada en el atributo 'species_data' escribimos una fila del 'csv'
                for spc in self.species_data:
                    writer.writerow(spc)
                

        # manejo excepciones al crear carpeta datos       
        except OSError as e:
            
            print('Error al crear la carpeta de datos')
            print("Descripcion:\n {descr}".format(descr=e))
                

                

