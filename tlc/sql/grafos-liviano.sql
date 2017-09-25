BEGIN;
DROP TABLE  IF EXISTS Average_costs;
CREATE TABLE Average_costs (
    city1 integer NOT NULL,
    city2 integer NOT NULL,
    cost integer NOT NULL
);


ALTER TABLE ONLY Average_costs
      ADD CONSTRAINT average_costs_fkey1 FOREIGN KEY (city1) REFERENCES City(id);
ALTER TABLE ONLY Average_costs
      ADD CONSTRAINT average_costs_fkey2 FOREIGN KEY (city2) REFERENCES City(id);


ALTER TABLE ONLY Average_costs
          ADD CONSTRAINT average_costs_pkey1 PRIMARY KEY (city1,city2);


COMMIT;
ANALYZE Average_costs;
