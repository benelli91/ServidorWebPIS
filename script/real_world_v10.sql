BEGIN;
DROP Table  IF EXISTS Travel;
DROP TABLE  IF EXISTS Currency ;
DROP TABLE  IF EXISTS City ;
DROP TABLE  IF EXISTS Country ;
DROP TABLE  IF EXISTS TravelAgencyAlias;
DROP TABLE  IF EXISTS TravelAgency;
DROP TABLE  IF EXISTS TravelType;

SET client_encoding = 'LATIN1';

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
    name text NOT NULL
);

COPY Currency (cod,name) FROM stdin;
USD	Dolar
ARS	Pesos Argentinos
EUR	Euros
UYU	Pesos Uruguayos
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
1	Aerolineas Argentinas	www.aerolineas.com.ar	1
2	Aeromás	www.aeromas.com	1
3	Air Class	www.airclass.com.uy	1
4	Air Europa	www.aireuropa.com	1
17	Air France	www.airfrance.com.uy	1
21	Amaszonas Uruguay	www.amaszonas.com	1
7	Amaszonas Paraguay	www.amaszonas.com	1
8	American Airlines	www.aa.com	1
9	Austral	www.austral.com.ar	1
10	Avianca	www.avianca.com	1
11	Azul	www.voeazul.com.br	1
12	Copa Airlines	www.copaair.com	1
13	Gol Linhas Aéreas	www.voegol.com	1
14	Iberia	www.iberia.com.uy	1
15	Latam Airlines	www.latam.com	1
16	Sky	www.skyairline.cl	1
5	Buquebus	www.buquebus.com.uy	2
18	Seacat	www.seacatcolonia.com	2
19	La Cacciola	www.cacciolaviajes.com	2
20	Colonia Express	coloniaexpress.com/uy/	2
6	Tres Cruces	www.trescruces.com.uy	3
22	COPAY	www.copay.coop	3
23	AGENCIA CENTRAL	www.agenciacentral.com.uy	3
24	Greyhound	www.greyhound.com	3
25	BERRUTTI	www.berruttiturismo.com	3
26	BRUNO	www.empresabruno.com.uy	3
27	CITA	www.cita.com.uy	3
28	NUNEZ	www.nunez.com.uy	3
29	COPSA	www.copsa.com.uy	3
30	CUT	www.cutcorporacion.com.uy	3
31	EGA	www.ega.com.uy	3
32	COTAR	www.grupocotar.com.uy	3
33	EMTUR	NULL	3
34	EL NORTEÑO	busdelnorte.com.uy	3
35	EL RAPIDO	www.el-rapido.com.ar	3
36	FLECHA BUS	www.flechabus.com.ar	3
37	INTERTUR	www.intertur.com.uy	3
38	JOTA ELE	www.jotaele.com.uy	3
39	NOSSAR	www.nossar.com.uy	3
40	RUTAS DEL SOL	turismorocha.gub.uy/destinos/rocha/empresas-de-transporte/rutas-del-sol	3
41	TTL	www.ttl.com.br	3
42	TURIL	www.turil.com.uy	3
43	TURISMAR	www.turismar.com.uy	3
44	Cauvi	www.retiro.com.ar/empresa/89/cauvi	3
45	Condor	condorestrella.com.ar	3
46	Pullman	www.ventapasajes.cl/pullmanbus	3
47	COIT	www.coitviajes.com.uy	3
48	COT	www.cot.com.uy	3
49	Ciudad de Gualeguay	www.ciudaddegualeguay.com	3
50	COTABU	NULL	3
51	COA	NULL	3
52	GABARD	NULL	3
53	Grupo Vittori	http://grupovittori.com.uy	3
54	TUR-ESTE	http://tureste.com/	3
55	POSADA	NULL	3
56	COTMI	NULL	3
57	Andesmar	https://www.andesmar.com/	3
58	Chevallier	http://nuevachevallier.com/	3
59	Alaska	https://www.alaskaair.com/	1
100	Google Flights	www.google.es/flights/#search	1
101	Central de Pasajes	www.centraldepasajes.com.ar	3
102	UruBus	www.urubus.com.uy	3
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
