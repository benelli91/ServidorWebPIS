BEGIN;
DROP Table  IF EXISTS Travel;
DROP TABLE  IF EXISTS Currency ;
DROP TABLE  IF EXISTS City ;
DROP TABLE  IF EXISTS Country ;
DROP TABLE  IF EXISTS TravelAgencyAlias;
DROP TABLE  IF EXISTS TravelAgency;
DROP TABLE  IF EXISTS TravelType;

SET client_encoding = 'UTF8';

CREATE TABLE Country (
    id character(3) NOT NULL,
    name text NOT NULL
);

CREATE TABLE City (
    id integer NOT NULL,
    country character(3) NOT NULL,
    name text NOT NULL,
    alias_flight character(3) NOT NULL,
    alias_port text NOT NULL,
    alias_bus text NOT NULL,
    airport boolean NOT NULL,
    port boolean NOT NULL,
    bus_station boolean NOT NULL
);

CREATE TABLE TravelType (
    traveltype integer NOT NULL,
    travelname text
);

CREATE TABLE Travel(
    departure timestamp NOT NULL,
    origin_city integer NOT NULL,
    destination_city integer NOT NULL,
    price real NOT NULL,
    duration integer NOT NULL,
    traveltype integer NOT NULL,
    webpage text NOT NULL,
    travel_agency integer,
    currency text NOT NULL,
    updated boolean NOT NULL,
    description text NOT NULL
);

ALTER TABLE Travel ADD COLUMN idtravel BIGSERIAL PRIMARY KEY;

CREATE TABLE TravelAgency(
    id integer NOT NULL,
    name text NOT NULL,
    reference text,
    traveltype integer NOT NULL
);

CREATE TABLE TravelAgencyAlias(
    id integer NOT NULL,
    traveltype integer NOT NULL,
    travelagency integer NOT NULL,
    alias text NOT NULL
);

CREATE TABLE Currency(
    cod character(3) NOT NULL,
    name text NOT NULL,
    base boolean NOT NULL,
    local boolean NOT NULL,
    divisor real NOT NULL,
    tablePosition integer NOT NULL
);

COPY Currency(cod, name, base, local, divisor, tablePosition) FROM stdin;
USD	Dólar	True	False	1	5
ARS	Peso Argentino	False	False	1	9
EUR	Euro	False	False	1	9
UYU	Peso Uruguayo	False	True	1	9
\.

COPY Country (id, name) FROM stdin;
URU	Uruguay
ARG	Argentina
USA	United States
PRY	Paraguay
BRA	Brasil
\.

COPY City(id, country, name, alias_flight, alias_port, alias_bus, airport, port, bus_station) FROM stdin;
1	URU	Artigas	NNN	NNN	Artigas	0	0	1
2	URU	Canelones	NNN	NNN	Canelones	0	0	1
3	URU	Colonia	NNN	COL	Colonia	0	1	1
4	URU	Durazno	NNN	NNN	Durazno	0	0	1
5	URU	Florida	NNN	NNN	Florida	0	0	1
6	URU	Fray Bentos	NNN	NNN	Fray Bentos	0	0	1
7	URU	Maldonado	NNN	NNN	Maldonado	0	0	1
8	URU	Melo	NNN	NNN	Melo	0	0	1
9	URU	Mercedes	NNN	NNN	Mercedes	0	0	1
10	URU	Minas	NNN	NNN	Minas	0	0	1
11	URU	Montevideo	MVD	MVD	Montevideo	1	1	1
12	URU	Paysandu	NNN	NNN	Paysandu	0	0	1
13	URU	Rivera	NNN	NNN	Rivera	0	0	1
14	URU	Rocha	NNN	NNN	Rocha	0	0	1
15	URU	Salto	NNN	NNN	Salto	0	0	1
16	URU	San Jose	NNN	NNN	San Jose	0	0	1
17	URU	Tacuarembo	NNN	NNN	Tacuarembo	0	0	1
18	URU	Treinta y Tres	NNN	NNN	Treinta y Tres	0	0	1
19	URU	Trinidad	NNN	NNN	Trinidad	0	0	1
20	ARG	Buenos Aires	BUE	BUE	Bueno Aires	1	1	1
21	ARG	Rosario	NNN	NNN	Rosario	0	0	1
22	ARG	Cordoba	NNN	NNN	Cordoba	0	0	1
23	ARG	La Plata	NNN	NNN	La Plata	0	0	1
24	ARG	Salta	NNN	NNN	Salta	0	0	1
25	ARG	Bariloche	BRC	NNN	Bariloche	1	0	1
26	ARG	Mar del Plata	NNN	NNN	Mar del Plata	0	0	1
27	ARG	Tucuman	NNN	NNN	Tucuman	0	0	1
28	ARG	Ushuaia	NNN	NNN	Ushuaia	0	0	1
29	ARG	Mendoza	NNN	NNN	Mendoza	0	0	1
30	USA	New York	NYC	NNN	New York	1	0	1
31	USA	Seattle	SEA	NNN	NNN	1	0	1
32	USA	Boston	NNN	NNN	NNN	0	0	0
33	USA	Los Angeles	NNN	NNN	NNN	0	0	0
34	USA	Chicago	NNN	NNN	NNN	0	0	0
35	USA	San Francisco	NNN	NNN	NNN	0	0	0
36	USA	Miami	MIA	NNN	Miami	1	0	1
37	USA	Atlanta	NNN	NNN	NNN	0	0	0
38	USA	Houston	NNN	NNN	NNN	0	0	0
39	USA	Washington	NNN	NNN	NNN	0	0	0
40	URU	Punta del Este	NNN	PDE	Punta del Este	0	1	1
41	PRY	Asuncion	ASU	NNN	Asuncion	1	0	1
42	BRA	Porto Alegre	POA	NNN	Porto Alegre	1	0	1
\.

COPY TravelType(traveltype, travelname) FROM stdin;
0	Generica
1	Plane
2	Boat
3	Bus
\.

COPY TravelAgency(id, name, reference, traveltype) FROM stdin;
0	Generica	NULL	0
1	Aerolineas Argentinas	http://www.aerolineas.com.ar	1
2	Aeromás	http://www.aeromas.com	1
3	Air Class	http://www.airclass.com.uy	1
4	Air Europa	http://www.aireuropa.com	1
17	Air France	http://www.airfrance.com.uy	1
21	Amaszonas Uruguay	http://www.amaszonas.com	1
7	Amaszonas Paraguay	http://www.amaszonas.com	1
8	American Airlines	http://www.aa.com	1
9	Austral	http://www.austral.com.ar	1
10	Avianca	http://www.avianca.com	1
11	Azul	http://www.voeazul.com.br	1
12	Copa Airlines	http://www.copaair.com	1
13	Gol Linhas Aéreas	http://www.voegol.com	1
14	Iberia	http://www.iberia.com.uy	1
15	Latam Airlines	http://www.latam.com	1
16	Sky	http://www.skyairline.cl	1
5	Buquebus	http://www.buquebus.com.uy	2
18	Seacat	http://www.seacatcolonia.com	2
19	La Cacciola	http://www.cacciolaviajes.com	2
20	Colonia Express	https://www.coloniaexpress.com	2
6	Tres Cruces	http://www.trescruces.com.uy	3
22	COPAY	http://www.copay.coop	3
23	AGENCIA CENTRAL	http://www.agenciacentral.com.uy	3
24	Greyhound	http://www.greyhound.com	3
25	BERRUTTI	http://www.berruttiturismo.com	3
26	BRUNO	http://www.empresabruno.com.uy	3
27	CITA	http://www.cita.com.uy	3
28	NUNEZ	http://www.nunez.com.uy	3
29	COPSA	http://www.copsa.com.uy	3
30	CUT	http://www.cutcorporacion.com.uy	3
31	EGA	http://www.ega.com.uy	3
32	COTAR	http://www.grupocotar.com.uy	3
33	EMTUR	NULL	3
34	EL NORTEÑO	http://busdelnorte.com.uy	3
35	EL RAPIDO	http://www.el-rapido.com.ar	3
36	FLECHA BUS	http://www.flechabus.com.ar	3
37	INTERTUR	http://www.intertur.com.uy	3
38	JOTA ELE	http://www.jotaele.com.uy	3
39	NOSSAR	http://www.nossar.com.uy	3
40	RUTAS DEL SOL	NULL	3
41	TTL	http://www.ttl.com.br	3
42	TURIL	http://www.turil.com.uy	3
43	TURISMAR	http://www.turismar.com.uy	3
44	Cauvi	NULL	3
45	Condor	http://condorestrella.com.ar	3
46	Pullman	NULL	3
47	COIT	http://www.coitviajes.com.uy	3
48	COT	http://www.cot.com.uy	3
49	Ciudad de Gualeguay	http://www.ciudaddegualeguay.com	3
50	COTABU	NULL	3
51	COA	NULL	3
52	GABARD	NULL	3
53	Grupo Vittori	http://grupovittori.com.uy	3
54	TUR-ESTE	http://tureste.com	3
55	POSADA	NULL	3
56	COTMI	NULL	3
57	Andesmar	https://www.andesmar.com	3
58	Chevallier	http://nuevachevallier.com	3
59	Alaska	https://www.alaskaair.com	1
60	United	https://www.united.com	1
61	JetBlue	https://www.jetblue.com	1
62	Delta	https://www.delta.com	1
63	Frontier	https://www.flyfrontier.com	1
64	Sun	https://www.suncountry.com/booking/search.html	1
65	Spirit	https://www.spirit.com	1
100	Google Flights	https://www.google.es/flights/#search	1
101	Central de Pasajes	https://www.centraldepasajes.com.ar	3
102	UruBus	https://www.urubus.com.uy	3
\.

COPY TravelAgencyAlias(id, traveltype, travelagency, alias) FROM stdin;
1	3	23	Chadre
2	3	23	Sabelin
3	3	28	Cynsa
4	3	30	Corporacion
5	3	32	Emdal
6	3	32	Chago
7	3	32	Expreso Chago
8	3	32	Expreso Minuano
9	3	32	Minuano
10	3	38	JL
11	3	40	Cromin
12	3	23	Grupo Agencia
13	3	31	Rutas del Plata
14	3	45	El Condor
15	3	46	Pullman Gral.Belgrano
16	1	15	LATAM
17	1	1	AR
18	1	15	LA
19	3	36	Flechabus
20	3	39	Nossar
21	3	26	BRUNO HNOS
22	3	30	ETA
23	3	53	PLAMA
24	3	53	ALONSO
25	1	59	Alaska Air
26	1	60	United Airlines
27	1	61	JetBlue Airways
28	1	62	DL
29	1	63	Frontier Airlines
30	1	64	Sun Country
31	1	64	Sun Country Airlines
32	1	64	Sun Airlines
33	1	8	American
34	1	60	UA
35	1	65	Spirit Airlines
36	1	8	AA
100	3	101	Central de Pasajes 2
101	3	101	Central de Pasajes 3
102	3	101	Central de Pasajes 4
103	3	101	Central de Pasajes 5
104	3	101	Central de Pasajes 6
\.

ALTER TABLE ONLY Country
    ADD CONSTRAINT country_pkey PRIMARY KEY (id);

ALTER TABLE ONLY City
    ADD CONSTRAINT city_fkey FOREIGN KEY (country) REFERENCES Country(id);

ALTER TABLE ONLY City
    ADD CONSTRAINT city_pkey PRIMARY KEY (id);

ALTER TABLE ONLY TravelType
    ADD CONSTRAINT traveltype_pkey PRIMARY KEY (traveltype);

ALTER TABLE ONLY Travel
    ADD CONSTRAINT travel_fkey1 FOREIGN KEY (traveltype) REFERENCES TravelType(traveltype);

ALTER TABLE ONLY Travel
    ADD CONSTRAINT travel_fkey2 FOREIGN KEY (origin_city) REFERENCES City(id);

ALTER TABLE ONLY Travel
    ADD CONSTRAINT travel_fkey3 FOREIGN KEY (destination_city) REFERENCES City(id);

ALTER TABLE ONLY TravelAgency
    ADD CONSTRAINT travelagency_pkey PRIMARY KEY (id);

ALTER TABLE ONLY TravelAgency
    ADD CONSTRAINT travelagency_fkey1 FOREIGN KEY (traveltype) REFERENCES TravelType(traveltype);

ALTER TABLE ONLY Currency
  ADD CONSTRAINT currency_pkey PRIMARY KEY (cod);

ALTER TABLE ONLY TravelAgencyAlias
  ADD CONSTRAINT travelagencyalias_pkey PRIMARY KEY (id);

ALTER TABLE ONLY TravelAgencyAlias
  ADD CONSTRAINT travelagencyalias_fkey1 FOREIGN KEY (traveltype) REFERENCES TravelType(traveltype);

ALTER TABLE ONLY TravelAgencyAlias
  ADD CONSTRAINT travelagencyalias_fkey2 FOREIGN KEY (travelagency) REFERENCES TravelAgency(id);

COMMIT;

ANALYZE City;
ANALYZE Country;
ANALYZE TravelType;
ANALYZE Travel;
ANALYZE TravelAgency;
ANALYZE Currency;
ANALYZE TravelAgencyAlias;
