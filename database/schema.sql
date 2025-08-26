-- Supabase Database Schema for Authentication System

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL CHECK (role IN ('super_admin', 'admin', 'admin_desa', 'admin_kelompok')),
    assigned_desa TEXT[],
    assigned_kelompok TEXT[],
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- User sessions table
CREATE TABLE user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    device_type TEXT,
    device_info TEXT,
    login_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Role permissions table
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL,
    menu_name TEXT NOT NULL,
    can_view BOOLEAN DEFAULT FALSE,
    can_create BOOLEAN DEFAULT FALSE,
    can_edit BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    UNIQUE(role, menu_name)
);

-- Insert default role permissions
INSERT INTO role_permissions (role, menu_name, can_view, can_create, can_edit, can_delete) VALUES
-- Super Admin - Full access to everything
('super_admin', 'Dashboard', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Input Data Muda-Mudi', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Manajemen Kegiatan', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Scan QR Absensi', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Pencarian Data', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Laporan', TRUE, TRUE, TRUE, TRUE),
('super_admin', 'Gabung Database', TRUE, TRUE, TRUE, TRUE),

-- Admin - Regional access
('admin', 'Dashboard', TRUE, FALSE, FALSE, FALSE),
('admin', 'Input Data Muda-Mudi', TRUE, TRUE, TRUE, TRUE),
('admin', 'Manajemen Kegiatan', TRUE, TRUE, TRUE, TRUE),
('admin', 'Scan QR Absensi', TRUE, TRUE, FALSE, FALSE),
('admin', 'Pencarian Data', TRUE, FALSE, FALSE, FALSE),
('admin', 'Laporan', TRUE, FALSE, FALSE, FALSE),

-- Admin Desa - Desa specific access
('admin_desa', 'Dashboard', TRUE, FALSE, FALSE, FALSE),
('admin_desa', 'Input Data Muda-Mudi', TRUE, TRUE, TRUE, FALSE),
('admin_desa', 'Manajemen Kegiatan', TRUE, FALSE, FALSE, FALSE),
('admin_desa', 'Scan QR Absensi', TRUE, TRUE, FALSE, FALSE),
('admin_desa', 'Pencarian Data', TRUE, FALSE, FALSE, FALSE),
('admin_desa', 'Laporan', TRUE, FALSE, FALSE, FALSE),

-- Admin Kelompok - Kelompok specific access
('admin_kelompok', 'Dashboard', TRUE, FALSE, FALSE, FALSE),
('admin_kelompok', 'Input Data Muda-Mudi', TRUE, TRUE, TRUE, FALSE),
('admin_kelompok', 'Scan QR Absensi', TRUE, TRUE, FALSE, FALSE),
('admin_kelompok', 'Pencarian Data', TRUE, FALSE, FALSE, FALSE);

-- Insert default super admin user (password: admin123)
INSERT INTO users (username, password_hash, email, role, assigned_desa, assigned_kelompok, status) VALUES
('superadmin', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', 'admin@mudaii.com', 'super_admin', '{}', '{}', 'active');

-- Insert sample users for testing
INSERT INTO users (username, password_hash, email, role, assigned_desa, assigned_kelompok, status, created_by) VALUES
('admin_bandara', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', 'bandara@mudaii.com', 'admin_desa', '{"BANDARA"}', '{"PRIMA", "RAWA LELE", "KAMPUNG DURI"}', 'active', 1),
('admin_cengkareng', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', 'cengkareng@mudaii.com', 'admin_desa', '{"CENGKARENG"}', '{"FAJAR A", "FAJAR B", "FAJAR C"}', 'active', 1),
('admin_prima', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qm', 'prima@mudaii.com', 'admin_kelompok', '{"BANDARA"}', '{"PRIMA"}', 'active', 1);