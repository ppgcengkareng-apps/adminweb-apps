class PermissionManager:
    def __init__(self, login_manager):
        self.login_manager = login_manager
        
        # Define menu permissions mapping
        self.menu_permissions = {
            'dashboard': 'Dashboard',
            'input_data': 'Input Data Muda-Mudi',
            'manajemen_kegiatan': 'Manajemen Kegiatan',
            'scan_qr': 'Scan QR Absensi',
            'pencarian_data': 'Pencarian Data',
            'laporan': 'Laporan',
            'gabung_database': 'Gabung Database'
        }
    
    def can_access_menu(self, menu_key):
        """Check if user can access a specific menu"""
        if not self.login_manager.is_logged_in():
            return False
        
        menu_name = self.menu_permissions.get(menu_key)
        if not menu_name:
            return True  # Allow access to unmapped menus by default
        
        return self.login_manager.has_permission(menu_name, 'view')
    
    def can_create_data(self, menu_key):
        """Check if user can create data in a specific menu"""
        if not self.login_manager.is_logged_in():
            return False
        
        menu_name = self.menu_permissions.get(menu_key)
        if not menu_name:
            return True
        
        return self.login_manager.has_permission(menu_name, 'create')
    
    def can_edit_data(self, menu_key):
        """Check if user can edit data in a specific menu"""
        if not self.login_manager.is_logged_in():
            return False
        
        menu_name = self.menu_permissions.get(menu_key)
        if not menu_name:
            return True
        
        return self.login_manager.has_permission(menu_name, 'edit')
    
    def can_delete_data(self, menu_key):
        """Check if user can delete data in a specific menu"""
        if not self.login_manager.is_logged_in():
            return False
        
        menu_name = self.menu_permissions.get(menu_key)
        if not menu_name:
            return True
        
        return self.login_manager.has_permission(menu_name, 'delete')
    
    def filter_desa_options(self, desa_list):
        """Filter desa options based on user permissions"""
        if not self.login_manager.is_logged_in():
            return []
        
        accessible_desa = self.login_manager.get_accessible_desa()
        if not accessible_desa:  # If empty, user can access all
            return desa_list
        
        return [desa for desa in desa_list if desa in accessible_desa]
    
    def filter_kelompok_options(self, kelompok_list):
        """Filter kelompok options based on user permissions"""
        if not self.login_manager.is_logged_in():
            return []
        
        accessible_kelompok = self.login_manager.get_accessible_kelompok()
        if not accessible_kelompok:  # If empty, user can access all
            return kelompok_list
        
        return [kelompok for kelompok in kelompok_list if kelompok in accessible_kelompok]
    
    def get_data_filter_clause(self):
        """Get SQL WHERE clause for filtering data based on user permissions"""
        if not self.login_manager.is_logged_in():
            return "1=0"  # No access
        
        user = self.login_manager.get_current_user()
        if user and user.get('role') == 'super_admin':
            return "1=1"  # Full access
        
        accessible_desa = self.login_manager.get_accessible_desa()
        accessible_kelompok = self.login_manager.get_accessible_kelompok()
        
        conditions = []
        
        if accessible_desa:
            desa_condition = "desa IN ({})".format(
                ','.join([f"'{desa}'" for desa in accessible_desa])
            )
            conditions.append(desa_condition)
        
        if accessible_kelompok:
            kelompok_condition = "kelompok IN ({})".format(
                ','.join([f"'{kelompok}'" for kelompok in accessible_kelompok])
            )
            conditions.append(kelompok_condition)
        
        if conditions:
            return " OR ".join(conditions)
        else:
            return "1=0"  # No access if no areas assigned
    
    def can_access_participant_data(self, desa, kelompok):
        """Check if user can access specific participant data"""
        if not self.login_manager.is_logged_in():
            return False
        
        # Check desa access
        if desa and not self.login_manager.can_access_desa(desa):
            return False
        
        # Check kelompok access
        if kelompok and not self.login_manager.can_access_kelompok(kelompok):
            return False
        
        return True
    
    def get_user_info_display(self):
        """Get formatted user info for display"""
        if not self.login_manager.is_logged_in():
            return "Tidak login"
        
        user = self.login_manager.get_current_user()
        if not user:
            return "Tidak login"
        
        role_display = {
            'super_admin': 'Super Admin',
            'admin': 'Admin Regional',
            'admin_desa': 'Admin Desa',
            'admin_kelompok': 'Admin Kelompok'
        }
        
        role = role_display.get(user.get('role', ''), user.get('role', ''))
        username = user.get('username', '')
        
        return f"{username} ({role})"
    
    def get_accessible_areas_display(self):
        """Get formatted accessible areas for display"""
        if not self.login_manager.is_logged_in():
            return ""
        
        user = self.login_manager.get_current_user()
        if user and user.get('role') == 'super_admin':
            return "Akses: Semua Area"
        
        accessible_desa = self.login_manager.get_accessible_desa()
        accessible_kelompok = self.login_manager.get_accessible_kelompok()
        
        areas = []
        if accessible_desa:
            areas.append(f"Desa: {', '.join(accessible_desa[:3])}")
            if len(accessible_desa) > 3:
                areas[-1] += f" (+{len(accessible_desa)-3} lainnya)"
        
        if accessible_kelompok:
            areas.append(f"Kelompok: {', '.join(accessible_kelompok[:2])}")
            if len(accessible_kelompok) > 2:
                areas[-1] += f" (+{len(accessible_kelompok)-2} lainnya)"
        
        return "Akses: " + " | ".join(areas) if areas else "Akses: Terbatas"