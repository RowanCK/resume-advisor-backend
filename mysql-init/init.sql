-- init.sql

CREATE DATABASE IF NOT EXISTS resume_advisor;
USE resume_advisor;

-- ---------- Core Tables ----------

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(20),
    location VARCHAR(30),
    password VARCHAR(200) NOT NULL,
    github VARCHAR(50),
    linkedin VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    title VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    creation_date DATE NOT NULL,
    last_updated DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cover_letters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    creation_date DATE NOT NULL,
    last_updated DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS education (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school VARCHAR(50) NOT NULL,
    program VARCHAR(50),
    degree VARCHAR(50),
    gpa DOUBLE,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(50) NOT NULL,
    start_date DATE,
    end_date DATE,
    description VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_title VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_responsibilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    work_exp_id INT NOT NULL,
    responsibility TEXT NOT NULL,
    FOREIGN KEY (work_exp_id) REFERENCES work_experiences(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    location TEXT,
    industry VARCHAR(50),
    website TEXT
);

CREATE TABLE IF NOT EXISTS job_postings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    company_id INT NOT NULL,
    description TEXT,
    job_location VARCHAR(50),
    posted_date DATE,
    close_date DATE,
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    requirement VARCHAR(50) NOT NULL,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS user_skill_map (
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency INT,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ---------- Indexes for Performance ----------

CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_education_user ON education(user_id);
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_work_experiences_user ON work_experiences(user_id);
CREATE INDEX idx_work_responsibilities_exp ON work_responsibilities(work_exp_id);
CREATE INDEX idx_job_postings_company ON job_postings(company_id);
CREATE INDEX idx_job_requirements_job ON job_requirements(job_id);
CREATE INDEX idx_user_skill_map_user ON user_skill_map(user_id);
CREATE INDEX idx_user_skill_map_skill ON user_skill_map(skill_id);