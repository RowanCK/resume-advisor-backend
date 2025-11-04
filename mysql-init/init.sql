-- init.sql

CREATE DATABASE IF NOT EXISTS resume_advisor;
USE resume_advisor;

-- ---------- Users ----------
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    email VARCHAR(255) NOT NULL UNIQUE,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------- User Content Library ----------
CREATE TABLE IF NOT EXISTS lib_experiences (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location TEXT,
    summary TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lib_exp_bullets (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    experience_id BIGINT NOT NULL,
    position INT NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (experience_id) REFERENCES lib_experiences(id)
);

CREATE TABLE IF NOT EXISTS lib_educations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    school TEXT NOT NULL,
    degree TEXT,
    program TEXT,
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3,2),
    location TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lib_projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    start_date DATE,
    end_date DATE,
    summary TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lib_proj_bullets (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL,
    position INT NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES lib_projects(id)
);

CREATE TABLE IF NOT EXISTS lib_skills (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS lib_skill_tags (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    item_type TEXT NOT NULL,
    item_id BIGINT NOT NULL,
    FOREIGN KEY (skill_id) REFERENCES lib_skills(id)
);

-- ---------- Resume Documents ----------
CREATE TABLE IF NOT EXISTS resumes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    template_key TEXT DEFAULT 'classic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS resume_sections (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    type TEXT NOT NULL,
    title_override TEXT,
    position INT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

CREATE INDEX idx_resume_sections_order ON resume_sections(resume_id, position);

CREATE TABLE IF NOT EXISTS resume_experiences (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    lib_experience_id BIGINT NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (lib_experience_id) REFERENCES lib_experiences(id)
);

CREATE INDEX idx_resume_experiences_order ON resume_experiences(resume_id, position);

CREATE TABLE IF NOT EXISTS resume_exp_bullet_overrides (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_experience_id BIGINT NOT NULL,
    lib_exp_bullet_id BIGINT NOT NULL,
    position INT NOT NULL,
    text_override TEXT,
    FOREIGN KEY (resume_experience_id) REFERENCES resume_experiences(id),
    FOREIGN KEY (lib_exp_bullet_id) REFERENCES lib_exp_bullets(id)
);

CREATE TABLE IF NOT EXISTS resume_educations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    lib_education_id BIGINT NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (lib_education_id) REFERENCES lib_educations(id)
);

CREATE TABLE IF NOT EXISTS resume_projects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    lib_project_id BIGINT NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (lib_project_id) REFERENCES lib_projects(id)
);

CREATE INDEX idx_resume_projects_order ON resume_projects(resume_id, position);

CREATE TABLE IF NOT EXISTS resume_proj_bullet_overrides (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_project_id BIGINT NOT NULL,
    lib_proj_bullet_id BIGINT NOT NULL,
    position INT NOT NULL,
    text_override TEXT,
    FOREIGN KEY (resume_project_id) REFERENCES resume_projects(id),
    FOREIGN KEY (lib_proj_bullet_id) REFERENCES lib_proj_bullets(id)
);

CREATE TABLE IF NOT EXISTS resume_skills (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL,
    lib_skill_id BIGINT NOT NULL,
    position INT NOT NULL,
    proficiency SMALLINT,
    FOREIGN KEY (resume_id) REFERENCES resumes(id),
    FOREIGN KEY (lib_skill_id) REFERENCES lib_skills(id)
);

CREATE TABLE IF NOT EXISTS resume_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    resume_id BIGINT NOT NULL UNIQUE,
    markdown TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS resume_theme_settings (
    resume_id BIGINT PRIMARY KEY,
    settings_json JSON,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);
