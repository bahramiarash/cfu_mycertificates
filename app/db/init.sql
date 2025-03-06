CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(100) NOT NULL,
    lname VARCHAR(100) NOT NULL,
    national_id VARCHAR(20) UNIQUE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    cert_name VARCHAR(255) NOT NULL,
    cert_file LONGBLOB NOT NULL,
    issue_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO users (fname, lname, national_id)
VALUES
('Ali', 'Hosseini', '1234567890'),
('Sara', 'Ahmadi', '9876543210');

INSERT INTO certificates (user_id, cert_name, cert_file, issue_date, expiration_date)
VALUES
(1, 'AWS Certified Developer', '/certs/aws_cert.svg', '2025-01-01', '2028-01-01'),
(1, 'Python Pro', '/certs/python_pro.svg', '2023-06-15', NULL),
(2, 'Google Cloud Architect', '/certs/gcp_cert.svg', '2024-01-10', '2027-01-10');
