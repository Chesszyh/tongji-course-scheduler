-- Read-only user
CREATE USER 'r_user'@'%' IDENTIFIED BY 'read_only_user_password';
GRANT SELECT ON tongji_course.* TO 'r_user'@'%';
FLUSH PRIVILEGES;

-- Write user
CREATE USER 'w_user'@'%' IDENTIFIED BY 'write_user_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON tongji_course.* TO 'w_user'@'%';
FLUSH PRIVILEGES;

-- Remote user
CREATE USER 'remote_user'@'<your_whitelisted_ip>' IDENTIFIED BY 'remote_user_password';
GRANT ALL PRIVILEGES ON tongji_course.* TO 'remote_user'@'<your_whitelisted_ip>';
FLUSH PRIVILEGES;