CREATE TABLE t_videos_people_detected (
    id SERIAL PRIMARY KEY,           
    file_path VARCHAR(255) NOT NULL, 
    send_alert_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	start_detected  VARCHAR(255) NOT NULL,
	end_detected VARCHAR(255) NOT NULL,
	imageb64 TEXT NOT NULL,
	to_email VARCHAR(255) NOT NULL
);

CREATE TABLE t_images_people_detected (
    id SERIAL PRIMARY KEY,           
    file_path VARCHAR(255) NOT NULL, 
    send_alert_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	imageb64 TEXT NOT NULL,
	to_email VARCHAR(255) NOT NULL
);

CREATE TABLE t_webcam_people_detected (
    id SERIAL PRIMARY KEY,           
    file_path VARCHAR(255) NOT NULL, 
    send_alert_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	start_timestamp  VARCHAR(255) NOT NULL,
	end_timestamp VARCHAR(255) NOT NULL,
	imageb64 TEXT NOT NULL,
	to_email VARCHAR(255) NOT NULL
);