# Define your item pipelines here

from itemadapter import ItemAdapter
import re

class EventscraperPipeline:
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        descrizione = adapter.get('descrizione')
        luogo = adapter.get('luogo')
        
        if descrizione:
            # Rimuovi i tag HTML e gli spazi bianchi extra
            descrizione = re.sub(r'<[^>]+>', '', descrizione)
            descrizione = re.sub(r'\s+', ' ', descrizione).strip()
            descrizione = descrizione.replace("\xa0", " ")
            adapter['descrizione'] = descrizione 
        
        # Strip whitespace da tutti i campi testuali
        for field_name in adapter.field_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()

                
        #gestisce la traduzione "orario non disponibile" in None
        if "orario" in adapter:
            raw_orario = adapter["orario"]
            if raw_orario and "orario non disponibile" in raw_orario.lower():
                adapter["orario"] = None  # Imposta su None se "orario non disponibile"
            elif raw_orario and "orari vari" in raw_orario.lower():
                adapter["orario"] = None  # Imposta su None se "orari vari"
            

            # Normalizza il formato dell'orario
            elif raw_orario:
                adapter["orario"] = self.normalize_time(raw_orario)

        if "prezzo" in adapter:
            adapter["prezzo"] = self.normalize_price(adapter["prezzo"])

        return item

    def normalize_time(self, raw_time):
        """
        Normalizza il formato degli orari estratti.
        Supporta diversi formati e li trasforma in un formato standard HH:MM - HH:MM.
        Se ci sono più intervalli, restituisce solo il primo.
        """
        
        if "orario non disponibile" in raw_time.strip().lower():
            return "Non disponibile"

        raw_time = raw_time.lower().strip()
        raw_time = re.sub(r'[,.]', ':', raw_time)  # Sostituisce punti e virgole con ":"

        # Cerca range di orari scritti con "dalle ... alle ..."
        match = re.search(r"dalle\s*(\d{1,2})\s*alle\s*(\d{1,2})", raw_time)
        if match:
            start_time = f"{int(match.group(1)):02d}:00"
            end_time = f"{int(match.group(2)):02d}:00"
            return f"{start_time} - {end_time}"

        # Cerca intervalli con il trattino o la "–" lunga (es. "10:30 - 18:00")
        match = re.search(r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})", raw_time)
        if match:
            return f"{match.group(1)} - {match.group(2)}"

        # Cerca più intervalli e seleziona solo il primo
        matches = re.findall(r"(\d{1,2}:\d{2})\s*[-–]?\s*(\d{1,2}:\d{2})", raw_time)
        if matches:
            # Prende solo il primo intervallo
            return f"{matches[0][0]} - {matches[0][1]}"

        # Cerca singoli orari e li formatta in HH:MM
        match = re.findall(r"\b\d{1,2}[:.,]?\d{0,2}\b", raw_time)
        if match:
            formatted_times = []
            for time in match:
                parts = re.split(r'[:.,]', time)
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                formatted_times.append(f"{hour:02d}:{minute:02d}")
            
            return formatted_times[0]  # Restituisce solo il primo orario trovato

        # Se non trova un formato riconosciuto, restituisce il testo originale
        return raw_time

    
    def normalize_price(self, raw_price):
        """
        Pulisce e normalizza il formato del prezzo.
        Supporta vari formati come "10 euro", "gratis", "a partire da...", "10€", etc.
        Restituisce un prezzo numerico (senza decimali) o "Gratis" se il prezzo è gratuito.
        """
        if not raw_price:
            return ""

        raw_price = raw_price.strip().lower()

        # cambiamenti di dicitura
        if "non disponibile" in raw_price or "consultare il sito" in raw_price:
            return "Non disponibile"
        elif "ingresso libero fino ad esaurimento posti" in raw_price or "ingresso gratuito" in raw_price or "ingresso libero" in raw_price or "gratis" in raw_price or "offerta libera" in raw_price:
            return "0"


        # Se c'è una forma tipo "a partire da...", prendiamo il numero
        match = re.search(r"a partire da\s*(\d+)\s*(€|euro)?", raw_price)
        if match:
            return f"{int(match.group(1))}€"

        # Cerca il prezzo con simbolo euro, es. 10€, 10 euro
        match = re.search(r"(\d+)\s*(€|euro)?", raw_price)
        if match:
            return f"{int(match.group(1))}€"

        # Se il prezzo è in formato numerico (senza simbolo)
        match = re.search(r"(\d+)", raw_price)
        if match:
            return f"{int(match.group(1))}€"

        # Se non trova nessun formato valido, restituiamo il testo originale
        return raw_price

    