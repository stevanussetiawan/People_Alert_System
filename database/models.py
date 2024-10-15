from database.postgre import postgreConnection

def insert_alert_image(data):
    query = """
        INSERT INTO t_images_people_detected
            (file_path, send_alert_at, imageb64, to_email)
        VALUES 
            (%s, %s, %s, %s)
    """
    SECTION = 'local'
    postgrecon = postgreConnection(SECTION)
    connection = postgrecon.connection
    cursor = connection.cursor()
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    connection.close()
    
    
def insert_alert_video(data):
    query = """
        INSERT INTO t_videos_people_detected 
            (file_path, send_alert_at, start_detected, end_detected, imageb64, to_email)
        VALUES 
            (%s, %s, %s, %s, %s, %s)
    """
    SECTION = 'local'
    postgrecon = postgreConnection(SECTION)
    connection = postgrecon.connection
    cursor = connection.cursor()
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    connection.close()
    
    
def insert_alert_webcam(data):
    query = """
        INSERT INTO t_webcam_people_detected 
            (send_alert_at, start_timestamp, end_timestamp, imageb64, to_email)
        VALUES 
            (%s, %s, %s, %s, %s)
    """
    SECTION = 'local'
    postgrecon = postgreConnection(SECTION)
    connection = postgrecon.connection
    cursor = connection.cursor()
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    connection.close()