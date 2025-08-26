const jwt = require('jsonwebtoken');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

const JWT_SECRET = process.env.JWT_SECRET;

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
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
      return res.status(403).json({ error: 'Akses ditolak. Hanya super admin yang bisa melihat daftar user.' });
    }

    // Get all users
    const { data: users, error } = await supabase
      .from('users')
      .select('id, username, email, role, assigned_desa, assigned_kelompok, status, created_at')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Get users error:', error);
      return res.status(500).json({ error: 'Gagal mengambil data user' });
    }

    res.status(200).json({
      success: true,
      data: users
    });

  } catch (error) {
    console.error('List users error:', error);
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Token tidak valid' });
    }
    res.status(500).json({ error: 'Internal server error' });
  }
}