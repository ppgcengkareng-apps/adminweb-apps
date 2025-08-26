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
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token tidak ditemukan' });
    }

    const token = authHeader.substring(7);
    
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      
      const { data: permissions, error: permError } = await supabase
        .from('role_permissions')
        .select('*')
        .eq('role', decoded.role);

      if (permError) {
        console.error('Permission error:', permError);
        return res.status(500).json({ error: 'Gagal mengambil permissions' });
      }

      const menuPermissions = {};
      permissions.forEach(perm => {
        menuPermissions[perm.menu_name] = {
          can_view: perm.can_view,
          can_create: perm.can_create,
          can_edit: perm.can_edit,
          can_delete: perm.can_delete
        };
      });

      res.status(200).json({
        success: true,
        data: {
          user: {
            id: decoded.userId,
            username: decoded.username,
            role: decoded.role,
            assigned_desa: decoded.assigned_desa,
            assigned_kelompok: decoded.assigned_kelompok
          },
          permissions: menuPermissions,
          accessible_areas: {
            desa: decoded.assigned_desa || [],
            kelompok: decoded.assigned_kelompok || []
          }
        }
      });

    } catch (jwtError) {
      return res.status(401).json({ error: 'Token tidak valid atau expired' });
    }

  } catch (error) {
    console.error('Permissions error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}