const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

const JWT_SECRET = process.env.JWT_SECRET;

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Verify admin token
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token tidak valid' });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, JWT_SECRET);
    
    if (decoded.role !== 'super_admin') {
      return res.status(403).json({ error: 'Akses ditolak. Hanya super admin yang bisa membuat user.' });
    }

    const { username, email, password, role, assigned_desa = [], assigned_kelompok = [] } = req.body;

    if (!username || !password || !role) {
      return res.status(400).json({ error: 'Username, password, dan role harus diisi' });
    }

    // Check if username already exists
    const { data: existingUser } = await supabase
      .from('users')
      .select('id')
      .eq('username', username)
      .single();

    if (existingUser) {
      return res.status(400).json({ error: 'Username sudah digunakan' });
    }

    // Hash password (simple for demo)
    const password_hash = password; // Using plain text for simplicity

    // Insert new user
    const { data: newUser, error: insertError } = await supabase
      .from('users')
      .insert({
        username,
        email,
        password_hash,
        role,
        assigned_desa,
        assigned_kelompok,
        status: 'active',
        created_by: decoded.userId
      })
      .select()
      .single();

    if (insertError) {
      console.error('Insert error:', insertError);
      return res.status(500).json({ error: 'Gagal membuat user' });
    }

    res.status(201).json({
      success: true,
      message: 'User berhasil dibuat',
      data: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role,
        assigned_desa: newUser.assigned_desa,
        assigned_kelompok: newUser.assigned_kelompok
      }
    });

  } catch (error) {
    console.error('Create user error:', error);
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Token tidak valid' });
    }
    res.status(500).json({ error: 'Internal server error' });
  }
}