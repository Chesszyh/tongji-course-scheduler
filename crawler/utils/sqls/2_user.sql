-- You are root user
-- Read-only user creation
CREATE USER 'r_user'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON tongji_course.* TO 'r_user'@'%';    -- %: allow from any host, change to 'localhost' / `172.17.0.1` (docker host) if needed
FLUSH PRIVILEGES;

-- Write user creation
CREATE USER 'w_user'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON tongji_course.* TO 'w_user'@'%';
FLUSH PRIVILEGES;