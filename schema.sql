PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE goods (
	id INTEGER NOT NULL,
	g_name VARCHAR,
	g_price VARCHAR,
	PRIMARY KEY (id)
);
CREATE TABLE sign (
	id INTEGER NOT NULL,
	name VARCHAR,
	password VARCHAR,
	req_id VARCHAR,
	openid VARCHAR,
	appkey VARCHAR,
	is_ok BOOLEAN,
	PRIMARY KEY (id),
	UNIQUE (openid),
	UNIQUE (req_id),
	CHECK (is_ok IN (0, 1))
);

CREATE TABLE orders (
	id INTEGER NOT NULL,
	order_num VARCHAR,
	good_id INTEGER,
	drawee VARCHAR,
	address VARCHAR,
	g_name VARCHAR,
	g_price VARCHAR,
	mobile VARCHAR,
	g_type VARCHAR,
	PRIMARY KEY (id),
	FOREIGN KEY(good_id) REFERENCES goods (id),
	UNIQUE (address),
	UNIQUE (order_num)
);
CREATE TABLE status (
	id INTEGER NOT NULL,
	req_id VARCHAR,
	status INTEGER,
	owner_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(owner_id) REFERENCES sign (id)
);
CREATE INDEX ix_goods_id ON goods (id);
CREATE INDEX ix_sign_id ON sign (id);
CREATE INDEX ix_status_id ON status (id);
COMMIT;
