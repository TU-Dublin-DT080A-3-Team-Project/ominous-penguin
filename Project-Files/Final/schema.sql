/*Initial creation scheme for simple database Creation*/
DROP TABLE IF EXISTS users;
CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	username TEXT NOT NULL,
	upassword TEXT NOT NULL
);
