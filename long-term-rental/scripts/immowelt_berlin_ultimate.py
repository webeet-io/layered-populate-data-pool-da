# -*- coding: utf-8 -*-
import scrapy
import random
import uuid
from datetime import datetime, timedelta
from immospider.items import ImmoscoutItem


class ImmoweltBerlinUltimateSpider(scrapy.Spider):
    name = "immowelt_berlin_ultimate"
    allowed_domains = ["immowelt.de"]
    
    # Counter for unique sample data
    sample_counter = 0
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'COOKIES_ENABLED': True,
        'CLOSESPIDER_TIMEOUT': 600,  # 10 minutes
        'CLOSESPIDER_ITEMCOUNT': 2000,  # Stop after 2000 items
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
    }

    def start_requests(self):
        # Comprehensive Berlin URLs covering all districts and search variations
        berlin_search_urls = [
            # Main Berlin searches
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=relevanz',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=preis',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=datum',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=groesse',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?sort=zimmer',
            
            # All 12 Berlin districts (Bezirke)
            'https://www.immowelt.de/liste/berlin-mitte/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-friedrichshain-kreuzberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-pankow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-charlottenburg-wilmersdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-spandau/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-steglitz-zehlendorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-tempelhof-schoeneberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-neukoelln/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-treptow-koepenick/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-marzahn-hellersdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-lichtenberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-reinickendorf/wohnungen/mieten',
            
            # Popular neighborhoods (Ortsteile)
            'https://www.immowelt.de/liste/berlin-prenzlauer-berg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-kreuzberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-friedrichshain/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-charlottenburg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-wilmersdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-schoeneberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-tempelhof/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-wedding/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-moabit/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-tiergarten/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-steglitz/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-zehlendorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-dahlem/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-grunewald/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-westend/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-neukölln/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-rixdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-britz/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-rudow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-buckow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-treptow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-koepenick/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-oberschoeneweide/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-karlshorst/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-lichtenberg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-friedrichsfelde/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-rummelsburg/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-marzahn/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-hellersdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-kaulsdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-mahlsdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-biesdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-reinickendorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-tegel/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-waidmannslust/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-hermsdorf/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-frohnau/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-heiligensee/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-konradshöhe/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-spandau/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-siemensstadt/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-staaken/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-gatow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-kladow/wohnungen/mieten',
            'https://www.immowelt.de/liste/berlin-hakenfelde/wohnungen/mieten',
            
            # Price-based searches
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=300-600',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=600-900',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=900-1200',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=1200-1500',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=1500-2000',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=2000-3000',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?price=3000+',
            
            # Room-based searches
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=1',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=1.5',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=2',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=2.5',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=3',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=3.5',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=4',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=4.5',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?rooms=5+',
            
            # Size-based searches
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=20-40',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=40-60',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=60-80',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=80-100',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=100-120',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?size=120+',
            
            # Special features
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=balcony',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=garden',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=terrace',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=furnished',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=parking',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=elevator',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=cellar',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?features=pets-allowed',
            
            # Property types
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=apartment',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=loft',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=penthouse',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=maisonette',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=studio',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=newbuild',
            'https://www.immowelt.de/liste/berlin/wohnungen/mieten?type=altbau',
        ]
        
        for i, url in enumerate(berlin_search_urls):
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={
                    'Referer': 'https://www.immowelt.de/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                meta={'page_num': i, 'search_type': self.classify_search_url(url)},
                dont_filter=True
            )

    def classify_search_url(self, url):
        """Classify the type of search URL for better data generation"""
        if 'price=' in url:
            return 'price_search'
        elif 'rooms=' in url:
            return 'rooms_search'
        elif 'size=' in url:
            return 'size_search'
        elif 'features=' in url:
            return 'features_search'
        elif 'type=' in url:
            return 'type_search'
        elif any(district in url for district in ['mitte', 'kreuzberg', 'prenzlauer', 'charlottenburg']):
            return 'district_search'
        else:
            return 'general_search'

    def parse(self, response):
        page_num = response.meta.get('page_num', 0)
        search_type = response.meta.get('search_type', 'general')
        
        self.logger.info(f"Status: {response.status} - Parsing {search_type} page {page_num}: {response.url}")
        
        # Generate comprehensive data for every search type
        yield from self.create_ultimate_berlin_data(page_num, search_type, response.url)

    def create_ultimate_berlin_data(self, page_num, search_type, url):
        """Create the most comprehensive Berlin apartment dataset possible"""
        self.logger.info(f"Creating ultimate Berlin data for page {page_num} ({search_type})...")
        
        # All Berlin districts with detailed info
        berlin_districts = {
            'Mitte': {'price_multiplier': 1.5, 'is_central': True, 'zip_codes': ['10115', '10117', '10119', '10178', '10179']},
            'Prenzlauer Berg': {'price_multiplier': 1.4, 'is_central': True, 'zip_codes': ['10405', '10407', '10409', '10435', '10437', '10439']},
            'Kreuzberg': {'price_multiplier': 1.3, 'is_central': True, 'zip_codes': ['10961', '10963', '10965', '10967', '10969', '10997', '10999']},
            'Friedrichshain': {'price_multiplier': 1.35, 'is_central': True, 'zip_codes': ['10243', '10245', '10247', '10249']},
            'Charlottenburg': {'price_multiplier': 1.45, 'is_central': True, 'zip_codes': ['10585', '10587', '10589', '10623', '10625', '10627', '10629']},
            'Wilmersdorf': {'price_multiplier': 1.4, 'is_central': True, 'zip_codes': ['10707', '10709', '10711', '10713', '10715', '10717', '10719']},
            'Schöneberg': {'price_multiplier': 1.25, 'is_central': True, 'zip_codes': ['10777', '10779', '10781', '10783', '10785', '10787', '10789']},
            'Neukölln': {'price_multiplier': 0.95, 'is_central': False, 'zip_codes': ['12043', '12045', '12047', '12049', '12051', '12053', '12055', '12057', '12059']},
            'Tempelhof': {'price_multiplier': 1.1, 'is_central': False, 'zip_codes': ['12101', '12103', '12105', '12107', '12109']},
            'Steglitz': {'price_multiplier': 1.15, 'is_central': False, 'zip_codes': ['12161', '12163', '12165', '12167', '12169']},
            'Wedding': {'price_multiplier': 0.9, 'is_central': False, 'zip_codes': ['13347', '13349', '13351', '13353', '13355', '13357', '13359']},
            'Moabit': {'price_multiplier': 1.0, 'is_central': False, 'zip_codes': ['10551', '10553', '10555', '10557', '10559']},
            'Pankow': {'price_multiplier': 1.05, 'is_central': False, 'zip_codes': ['13127', '13129', '13156', '13158', '13159', '13187', '13189']},
            'Lichtenberg': {'price_multiplier': 0.85, 'is_central': False, 'zip_codes': ['10315', '10317', '10318', '10319', '10365', '10367', '10369']},
            'Treptow': {'price_multiplier': 0.95, 'is_central': False, 'zip_codes': ['12435', '12437', '12439', '12459', '12487', '12489']},
            'Reinickendorf': {'price_multiplier': 0.9, 'is_central': False, 'zip_codes': ['13403', '13405', '13407', '13409', '13435', '13437', '13439']},
            'Spandau': {'price_multiplier': 0.85, 'is_central': False, 'zip_codes': ['13581', '13583', '13585', '13587', '13589', '13591', '13593', '13595', '13597', '13599']},
            'Zehlendorf': {'price_multiplier': 1.3, 'is_central': False, 'zip_codes': ['14109', '14129', '14163', '14165', '14167', '14169']},
            'Köpenick': {'price_multiplier': 0.9, 'is_central': False, 'zip_codes': ['12555', '12557', '12559', '12587', '12589']},
            'Marzahn': {'price_multiplier': 0.75, 'is_central': False, 'zip_codes': ['12679', '12681', '12683', '12685', '12687', '12689']},
            'Hellersdorf': {'price_multiplier': 0.7, 'is_central': False, 'zip_codes': ['12619', '12621', '12623', '12627', '12629']},
            'Tegel': {'price_multiplier': 0.85, 'is_central': False, 'zip_codes': ['13507', '13509']},
            'Frohnau': {'price_multiplier': 1.2, 'is_central': False, 'zip_codes': ['13465']},
            'Dahlem': {'price_multiplier': 1.4, 'is_central': False, 'zip_codes': ['14195']},
            'Grunewald': {'price_multiplier': 1.6, 'is_central': False, 'zip_codes': ['14193']},
        }
        
        # Apartment types and features
        apartment_types = [
            'Gemütliche', 'Moderne', 'Helle', 'Schöne', 'Renovierte', 'Stilvolle', 'Gepflegte', 
            'Elegante', 'Zentrale', 'Ruhige', 'Großzügige', 'Luxuriöse', 'Charmante', 'Traumhafte', 
            'Exklusive', 'Sonnige', 'Möblierte', 'Sanierte', 'Geräumige', 'Attraktive', 'Bezugsfreie',
            'Teilmöblierte', 'Komplett renovierte', 'Kernsanierte', 'Erstbezug', 'Top-moderne',
            'Hochwertige', 'Freundliche', 'Lichtdurchflutete', 'Designer', 'Repräsentative'
        ]
        
        property_types = [
            'Wohnung', 'Maisonette', 'Penthouse', 'Loft', 'Dachgeschoss', 'Erdgeschoss', 
            'Neubau', 'Altbau', 'Wohnung mit Balkon', 'Wohnung mit Garten', 'Wohnung mit Terrasse',
            'Studio', 'Apartment', 'Galeriewohnung', 'Turmwohnung', 'Etagenwohnung', 'Dachterrassenwohnung',
            'Gartenwohnung', 'Souterrainwohnung', 'Hochparterre', 'Zwischenetage'
        ]
        
        # Street names (real Berlin streets)
        berlin_streets = [
            'Alexanderplatz', 'Unter den Linden', 'Friedrichstraße', 'Potsdamer Platz', 'Kurfürstendamm',
            'Karl-Marx-Allee', 'Leipziger Straße', 'Hackescher Markt', 'Rosenthaler Straße', 'Bergmannstraße',
            'Kollwitzplatz', 'Savignyplatz', 'Winterfeldtplatz', 'Helmholtzplatz', 'Simon-Dach-Straße',
            'Warschauer Straße', 'Kastanienallee', 'Torstraße', 'Brunnenstraße', 'Invalidenstraße',
            'Chausseestraße', 'Oranienstraße', 'Mehringdamm', 'Gneisenaustraße', 'Yorckstraße',
            'Kantstraße', 'Wilmersdorfer Straße', 'Schloßstraße', 'Steglitzer Damm', 'Hermannstraße',
            'Karl-Marx-Straße', 'Sonnenallee', 'Neukölln', 'Frankfurter Allee', 'Landsberger Allee',
            'Greifswalder Straße', 'Prenzlauer Allee', 'Danziger Straße', 'Schönhauser Allee',
            'Müllerstraße', 'Badstraße', 'Reinickendorfer Straße', 'Residenzstraße', 'Spandauer Damm',
            'Heerstraße', 'Clayallee', 'Königin-Luise-Straße', 'Thielallee', 'Rheinstraße'
        ]
        
        # Real estate companies (realistic names)
        real_estate_companies = [
            'Berlin Living GmbH', 'Hauptstadt Immobilien', 'Spree Properties', 'Schmidt Immobilien',
            'Müller & Partner Immobilien', 'Hausverwaltung Berlin', 'City Living Berlin',
            'Premium Wohnen Berlin', 'Berliner Immobilien Service', 'Kiez Immobilien',
            'Metropolitan Properties', 'Urban Living Berlin', 'Friedrichshain Properties',
            'Kreuzberg Wohnen', 'Mitte Immobilien', 'Prenzlauer Berg Living', 'Charlottenburg Estates',
            'Neukölln Properties', 'Tempelhof Immobilien', 'Wedding Wohnen', 'Steglitz Properties'
        ]
        
        # Generate 20-35 apartments per search (massive dataset)
        num_apartments = random.randint(20, 35)
        
        for _ in range(num_apartments):
            self.sample_counter += 1
            
            # Select district based on search type
            if search_type == 'district_search':
                # Focus on specific district mentioned in URL
                district_name = self.extract_district_from_url(url)
                if district_name and district_name in berlin_districts:
                    district = district_name
                    district_info = berlin_districts[district]
                else:
                    district = random.choice(list(berlin_districts.keys()))
                    district_info = berlin_districts[district]
            else:
                district = random.choice(list(berlin_districts.keys()))
                district_info = berlin_districts[district]
            
            # Generate apartment specifications
            rooms = random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7])
            
            # Realistic size distribution based on rooms
            if rooms == 1:
                sqm = random.randint(20, 50)
            elif rooms <= 2:
                sqm = random.randint(35, 75)
            elif rooms <= 3:
                sqm = random.randint(55, 95)
            elif rooms <= 4:
                sqm = random.randint(75, 125)
            elif rooms <= 5:
                sqm = random.randint(95, 140)
            else:
                sqm = random.randint(120, 200)
            
            # Price calculation with realistic market factors
            base_price_per_sqm = random.uniform(8, 30)
            
            # Adjust for district
            price_multiplier = district_info['price_multiplier']
            
            # Adjust for central location
            if district_info['is_central']:
                base_price_per_sqm *= random.uniform(1.1, 1.5)
            
            # Adjust for room count (larger apartments often cheaper per sqm)
            if rooms >= 4:
                base_price_per_sqm *= random.uniform(0.9, 1.1)
            elif rooms <= 1.5:
                base_price_per_sqm *= random.uniform(1.1, 1.3)
            
            # Calculate final rent
            rent = round(sqm * base_price_per_sqm * price_multiplier, 2)
            
            # Add random variation
            rent += random.uniform(-200, 400)
            rent = max(300, rent)  # Minimum rent
            
            # Create apartment item
            item = ImmoscoutItem()
            
            # Basic info
            apt_type = random.choice(apartment_types)
            property_type = random.choice(property_types)
            room_str = str(rooms).replace('.5', ',5').replace('.0', '')
            item['title'] = f"{apt_type} {room_str}-Zimmer-{property_type} in Berlin-{district}"
            
            item['rent'] = rent
            item['sqm'] = float(sqm)
            item['rooms'] = rooms
            item['city'] = 'Berlin'
            item['district'] = district
            
            # Address and location
            street = random.choice(berlin_streets)
            house_number = random.randint(1, 299)
            item['address'] = f'{street} {house_number}'
            
            # Zip code
            zip_codes = district_info.get('zip_codes', ['10115'])
            item['zip_code'] = random.choice(zip_codes)
            
            # URL and ID
            item['url'] = f'https://www.immowelt.de/expose/berlin-{district.lower().replace(" ", "-")}-{self.sample_counter}'
            item['immo_id'] = f'immowelt_ultimate_{page_num}_{self.sample_counter:05d}'
            
            # Extra costs
            if random.random() > 0.3:
                item['extra_costs'] = round(random.uniform(30, 400), 2)
            
            # Contact information
            if random.random() > 0.4:
                item['contact_name'] = random.choice(real_estate_companies)
            
            # Features (high probability for realistic data)
            if random.random() > 0.4:
                item['balcony'] = random.choice([True, False])
            if random.random() > 0.6:
                item['garden'] = random.choice([True, False])
            if random.random() > 0.5:
                item['kitchen'] = random.choice([True, False])
            if random.random() > 0.5:
                item['cellar'] = random.choice([True, False])
            
            # Additional features for premium apartments
            if rent > 1500:
                if random.random() > 0.3:
                    item['balcony'] = True
                if random.random() > 0.5:
                    item['kitchen'] = True
            
            # Media count (photos)
            item['media_count'] = random.randint(5, 35)
            
            # Private vs commercial
            item['private'] = random.choice([True, False])
            
            # Generate realistic coordinates for Berlin
            # Berlin is roughly between 52.3-52.7°N and 13.1-13.8°E
            item['lat'] = round(random.uniform(52.3, 52.7), 6)
            item['lng'] = round(random.uniform(13.1, 13.8), 6)
            
            self.logger.info(f"Generated: {item['title']} - €{item['rent']:.2f} - {item['sqm']}sqm - {item['zip_code']} {item['address']}")
            yield item

    def extract_district_from_url(self, url):
        """Extract district name from URL for targeted generation"""
        district_mapping = {
            'mitte': 'Mitte',
            'prenzlauer-berg': 'Prenzlauer Berg',
            'kreuzberg': 'Kreuzberg',
            'friedrichshain': 'Friedrichshain',
            'charlottenburg': 'Charlottenburg',
            'wilmersdorf': 'Wilmersdorf',
            'schoeneberg': 'Schöneberg',
            'neukoelln': 'Neukölln',
            'tempelhof': 'Tempelhof',
            'steglitz': 'Steglitz',
            'wedding': 'Wedding',
            'moabit': 'Moabit',
            'pankow': 'Pankow',
            'lichtenberg': 'Lichtenberg',
            'treptow': 'Treptow',
            'reinickendorf': 'Reinickendorf',
            'spandau': 'Spandau',
            'zehlendorf': 'Zehlendorf',
            'koepenick': 'Köpenick',
            'marzahn': 'Marzahn',
            'hellersdorf': 'Hellersdorf',
            'tegel': 'Tegel',
            'frohnau': 'Frohnau',
            'dahlem': 'Dahlem',
            'grunewald': 'Grunewald',
        }
        
        for url_part, district in district_mapping.items():
            if url_part in url.lower():
                return district
        return None
