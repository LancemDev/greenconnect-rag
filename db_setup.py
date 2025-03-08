import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
connection_params = {
    'host': os.getenv('MYSQLHOST', 'mysql.railway.internal'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', 'gytdDlhBlQEGKMWZcTVluDdOjAhRwhlH'),
    'database': os.getenv('MYSQLDATABASE', 'railway'),
    'port': int(os.getenv('MYSQLPORT', 3306))
}

# Create tables
def setup_database():
    try:
        conn = pymysql.connect(**connection_params)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_type ENUM('individual', 'organization') NOT NULL,
                profile_img_url VARCHAR(255),
                verification_status ENUM('pending', 'verified') DEFAULT 'pending'
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                project_name VARCHAR(200) NOT NULL,
                project_type ENUM('forestry', 'agriculture', 'agroforestry', 'wetland', 'other') NOT NULL,
                location_lat DECIMAL(10, 8) NOT NULL,
                location_lng DECIMAL(11, 8) NOT NULL,
                area_size DECIMAL(10, 2) NOT NULL,
                area_unit ENUM('hectares', 'acres') NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('registered', 'assessing', 'verified', 'active', 'completed') DEFAULT 'registered',
                boundary_geojson JSON,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Carbon Assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                carbon_estimate DECIMAL(12, 2) NOT NULL,
                confidence_score DECIMAL(5, 2) NOT NULL,
                methodology VARCHAR(100) NOT NULL,
                data_sources JSON NOT NULL,
                ai_model_version VARCHAR(50) NOT NULL,
                verification_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                report_url VARCHAR(255),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')
        
        # Carbon Credits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carbon_credits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                assessment_id INT NOT NULL,
                credit_amount DECIMAL(12, 2) NOT NULL,
                issuance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATE,
                certificate_id VARCHAR(100) UNIQUE NOT NULL,
                status ENUM('available', 'reserved', 'sold', 'expired') DEFAULT 'available',
                price_per_credit DECIMAL(10, 2),
                verification_document_url VARCHAR(255),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (assessment_id) REFERENCES carbon_assessments(id) ON DELETE CASCADE
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                credit_id INT NOT NULL,
                buyer_id INT NOT NULL,
                seller_id INT NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                price_per_unit DECIMAL(10, 2) NOT NULL,
                total_price DECIMAL(12, 2) NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
                FOREIGN KEY (credit_id) REFERENCES carbon_credits(id) ON DELETE CASCADE,
                FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Satellite Monitoring Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS satellite_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                capture_date DATE NOT NULL,
                ndvi_value DECIMAL(5, 4),
                land_cover_classification VARCHAR(50),
                cloud_cover_percentage DECIMAL(5, 2),
                source VARCHAR(50) NOT NULL,
                raw_data_url VARCHAR(255),
                processed_data_url VARCHAR(255),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')
        
        # AI Verification Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_verification_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                assessment_id INT,
                verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used VARCHAR(100) NOT NULL,
                input_data JSON,
                output_result JSON,
                confidence_score DECIMAL(5, 2),
                verification_type ENUM('initial', 'periodic', 'final') NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (assessment_id) REFERENCES carbon_assessments(id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        print("Database setup completed successfully")
        
    except Exception as e:
        print(f"Database setup error: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()