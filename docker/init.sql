CREATE TABLE server (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    channel_notification_id VARCHAR(30)
);

CREATE TABLE race (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game VARCHAR(100),
    status ENUM('pause', 'en_cours', 'terminé') DEFAULT 'pause',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_end DATETIME DEFAULT NULL,
    server_id BIGINT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES server(discord_id) ON DELETE CASCADE
);

CREATE TABLE race_milestone (
    id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT NOT NULL,
    name TEXT NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (race_id) REFERENCES race(id) ON DELETE CASCADE
);

CREATE TABLE race_event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT NOT NULL,
    name TEXT NOT NULL,
    is_positive BOOLEAN NOT NULL,
    FOREIGN KEY (race_id) REFERENCES race(id) ON DELETE CASCADE
);

CREATE TABLE race_ranking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    race_id INT NOT NULL,
    player_name TEXT NOT NULL,
    position INTEGER NOT NULL,
    milestone_position INT DEFAULT 0,
    FOREIGN KEY (race_id) REFERENCES race(id) ON DELETE CASCADE
);

CREATE TABLE profil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    private_channel_id varchar(30),
    server_id BIGINT NOT NULL,
    FOREIGN KEY (server_id) REFERENCES server(discord_id) ON DELETE CASCADE
);

CREATE TABLE profil_race (
    profil_id INT NOT NULL,
    race_id INT NOT NULL,
    PRIMARY KEY (profil_id, race_id),
    FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE,
    FOREIGN KEY (race_id) REFERENCES race(id) ON DELETE CASCADE
);
