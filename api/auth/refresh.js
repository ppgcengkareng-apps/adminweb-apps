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
    const { refresh_token } = req.body;

    if (!refresh_token) {
      return res.status(400).json({ error: 'Refresh token harus disediakan' });
    }

    try {
      const decoded = jwt.verify(refresh_token, REFRESH_SECRET);
      
      // Get user data
      const { data: user, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('id', decoded.userId)
        .eq('status', 'active')
        .single();

      if (userError || !user) {
        return res.status(401).json({ error: 'User tidak ditemukan atau tidak aktif' });
      }

      // Generate new access token
      const newAccessToken = jwt.sign(
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

      // Update session activity
      await supabase
        .from('user_sessions')
        .update({ last_activity: new Date().toISOString() })
        .eq('user_id', user.id)
        .eq('is_active', true);

      res.status(200).json({
        success: true,
        message: 'Token berhasil diperbarui',
        data: {
          access_token: newAccessToken,
          user: {
            id: user.id,
            username: user.username,
            role: user.role,
            assigned_desa: user.assigned_desa,
            assigned_kelompok: user.assigned_kelompok
          }
        }
      });

    } catch (jwtError) {
      return res.status(401).json({ error: 'Refresh token tidak valid atau expired' });
    }

  } catch (error) {
    console.error('Refresh error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}