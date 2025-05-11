CREATE TABLE server (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    channel_notification_id VARCHAR(30)
);

CREATE TABLE race (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    server_id INT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE
);

CREATE TABLE profil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    server_id INT NOT NULL,
    race_id INT DEFAULT NULL,
    FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE,
    FOREIGN KEY (race_id) REFERENCES race(id) ON DELETE SET NULL
);
