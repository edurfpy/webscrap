# A mi hermano Enrique y a su grupo de senderismo Ayuco.
# Por la recuperación de los montes de Gran Canaria.
# Para que no vuelva a pasar nunca mas.


# importamos clase 'SpeciesScraper' del archivo 'scraper.py' en la misma carpeta
from scraper import SpeciesScraper

# instanciamos objeto SpeciesScraper
scraper = SpeciesScraper()

# realizamos el 'escaneo' y guardamos la informacion
scraper.scrape()
scraper.create_csv()

