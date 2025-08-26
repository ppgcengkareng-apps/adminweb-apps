# Sistem Autentikasi Muda-Mudi

Sistem autentikasi terintegrasi untuk aplikasi manajemen Muda-Mudi dengan role-based access control.

## 🏗️ Arsitektur Sistem

- **Backend API**: Vercel Serverless Functions (Node.js)
- **Database**: Supabase (PostgreSQL)
- **Desktop App**: Python Tkinter dengan integrasi autentikasi
- **Authentication**: JWT tokens dengan refresh mechanism

## 🚀 Setup dan Deployment

### 1. Setup Supabase Database

1. Buat project baru di [Supabase](https://supabase.com)
2. Jalankan script SQL dari `database/schema.sql` di SQL Editor
3. Catat URL dan Anon Key dari Settings > API

### 2. Deploy API ke Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Install dependencies:
```bash
npm install
```

3. Setup environment variables di Vercel:
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add JWT_SECRET
vercel env add REFRESH_SECRET
```

4. Deploy:
```bash
vercel --prod
```

### 3. Setup Python Desktop App

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Update API URL di `auth/login_manager.py`:
```python
self.api_base_url = "https://your-vercel-app.vercel.app"
```

3. Jalankan aplikasi:
```bash
python main_with_auth.py
```

## 👥 User Roles dan Permissions

### Super Admin
- **Username**: `superadmin`
- **Password**: `admin123` (ganti setelah login pertama)
- **Akses**: Semua fitur dan data

### Admin Desa
- **Akses**: Data dalam desa yang ditugaskan
- **Permissions**: Input, edit data peserta; scan QR; lihat laporan

### Admin Kelompok
- **Akses**: Data dalam kelompok yang ditugaskan
- **Permissions**: Input, edit data peserta; scan QR

## 🔐 Keamanan

- JWT tokens dengan expiry 30 menit
- Refresh tokens dengan expiry 7 hari
- Password hashing dengan bcrypt
- Encrypted token storage di desktop app
- Row-level security di database
- Rate limiting pada API endpoints

## 📱 Fitur Desktop App

### Sebelum Login
- Login screen dengan validasi
- Connection status check
- Remember me functionality

### Setelah Login
- User info display di header
- Menu filtering berdasarkan role
- Data filtering berdasarkan area assignment
- Automatic token refresh
- Secure logout

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/verify` - Verify token validity

### User Management
- `GET /api/user/permissions` - Get user permissions

## 🔧 Konfigurasi

### Environment Variables
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
JWT_SECRET=your-jwt-secret
REFRESH_SECRET=your-refresh-secret
```

### Database Schema
- `users` - User accounts dan role assignments
- `user_sessions` - Active user sessions
- `role_permissions` - Role-based permissions

## 📊 Monitoring

### Session Management
- Track active sessions per user
- Device information logging
- Automatic cleanup of old sessions

### Security Logging
- Failed login attempts
- Token refresh events
- Permission violations

## 🚨 Troubleshooting

### Connection Issues
1. Check internet connection
2. Verify API URL di login_manager.py
3. Check Vercel deployment status

### Authentication Errors
1. Verify Supabase credentials
2. Check JWT secret configuration
3. Ensure database schema is up to date

### Permission Issues
1. Check user role assignments
2. Verify role_permissions table
3. Check area assignments (desa/kelompok)

## 📝 Development

### Local Development
1. Setup local Supabase instance atau gunakan cloud
2. Update environment variables
3. Run `vercel dev` untuk local API testing

### Adding New Permissions
1. Update `role_permissions` table
2. Modify `permission_manager.py`
3. Update UI components dengan permission checks

## 🔄 Updates dan Maintenance

### Database Migrations
- Backup database sebelum update
- Test migrations di staging environment
- Update schema.sql untuk deployments baru

### Security Updates
- Rotate JWT secrets secara berkala
- Update dependencies
- Monitor untuk security vulnerabilities

## 📞 Support

Untuk bantuan teknis atau pertanyaan:
- Check troubleshooting guide
- Review logs di Vercel dashboard
- Check Supabase logs untuk database issues