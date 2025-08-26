const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

const JWT_SECRET = process.env.JWT_SECRET;
const REFRESH_SECRET = process.env.REFRESH_SECRET;

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { username, password, device_type = 'desktop', device_info = 'Python App' } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username dan password harus diisi' });
    }

    const { data: user, error: userError } = await supabase
      .from('users')
      .select('*')
      .eq('username', username)
      .eq('status', 'active')
      .single();

    if (userError || !user) {
      return res.status(401).json({ error: 'Username atau password salah' });
    }

    const isValidPassword = await bcrypt.compare(password, user.password_hash);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Username atau password salah' });
    }

    const accessToken = jwt.sign(
      { 
        userId: user.id, 
        username: user.username, 
        role: user.role,
        assigned_desa: user.assigned_desa,
        assigned_kelompok: user.assigned_kelompok
      },
      JWT_SECRET,
      { expiresIn: '30m' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id, username: user.username },
      REFRESH_SECRET,
      { expiresIn: '7d' }
    );

    const sessionId = `session_${user.id}_${Date.now()}`;
    await supabase
      .from('user_sessions')
      .insert({
        session_id: sessionId,
        user_id: user.id,
        device_type,
        device_info,
        login_time: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        is_active: true
      });

    res.status(200).json({
      success: true,
      message: 'Login berhasil',
      data: {
        access_token: accessToken,
        refresh_token: refreshToken,
        session_id: sessionId,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          assigned_desa: user.assigned_desa,
          assigned_kelompok: user.assigned_kelompok
        }
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}