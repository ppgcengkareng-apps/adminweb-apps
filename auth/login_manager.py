import requests
import json
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

class LoginManager:
    def __init__(self, api_base_url="https://adminweb-apps.vercel.app"):
        self.api_base_url = api_base_url
        self.token_file = "auth_tokens.dat"
        self.key_file = "auth.key"
        self.current_user = None
        self.access_token = None
        self.refresh_token = None
        self.permissions = {}
        self.accessible_areas = {}
        
        self._init_encryption()
        self._load_tokens()
    
    def _init_encryption(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher = Fernet(self.key)
    
    def _save_tokens(self):
        if self.access_token and self.refresh_token:
            token_data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'user': self.current_user,
                'permissions': self.permissions,
                'accessible_areas': self.accessible_areas,
                'saved_at': datetime.now().isoformat()
            }
            
            encrypted_data = self.cipher.encrypt(json.dumps(token_data).encode())
            with open(self.token_file, 'wb') as f:
                f.write(encrypted_data)
    
    def _load_tokens(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                token_data = json.loads(decrypted_data.decode())
                
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                self.current_user = token_data.get('user')
                self.permissions = token_data.get('permissions', {})
                self.accessible_areas = token_data.get('accessible_areas', {})
                
                saved_at = datetime.fromisoformat(token_data.get('saved_at'))
                if datetime.now() - saved_at > timedelta(days=6):
                    self._clear_tokens()
                    
            except Exception as e:
                print(f"Error loading tokens: {e}")
                self._clear_tokens()
    
    def _clear_tokens(self):
        self.access_token = None
        self.refresh_token = None
        self.current_user = None
        self.permissions = {}
        self.accessible_areas = {}
        
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
    
    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.api_base_url}/api/auth/login",
                json={
                    'username': username,
                    'password': password,
                    'device_type': 'desktop',
                    'device_info': 'Python Tkinter App'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.access_token = data['data']['access_token']
                    self.refresh_token = data['data']['refresh_token']
                    self.current_user = data['data']['user']
                    
                    self._load_permissions()
                    self._save_tokens()
                    
                    return True, "Login berhasil"
                else:
                    return False, data.get('error', 'Login gagal')
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Login gagal')
                
        except requests.exceptions.Timeout:
            return False, "Koneksi timeout. Periksa koneksi internet Anda."
        except requests.exceptions.ConnectionError:
            return False, "Tidak dapat terhubung ke server. Periksa koneksi internet Anda."
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _load_permissions(self):
        if not self.access_token:
            return
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/user/permissions",
                headers={'Authorization': f'Bearer {self.access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.permissions = data['data']['permissions']
                    self.accessible_areas = data['data']['accessible_areas']
                    
        except Exception as e:
            print(f"Error loading permissions: {e}")
    
    def verify_token(self):
        if not self.access_token:
            return False
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/auth/verify",
                headers={'Authorization': f'Bearer {self.access_token}'},
                timeout=10
            )
            
            return response.status_code == 200 and response.json().get('valid', False)
            
        except Exception:
            return False
    
    def refresh_access_token(self):
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/auth/refresh",
                json={'refresh_token': self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.access_token = data['data']['access_token']
                    self.current_user = data['data']['user']
                    self._save_tokens()
                    return True
                    
        except Exception as e:
            print(f"Error refreshing token: {e}")
        
        return False
    
    def logout(self):
        self._clear_tokens()
        return True
    
    def is_logged_in(self):
        if not self.access_token:
            return False
        
        if self.verify_token():
            return True
        
        if self.refresh_access_token():
            return True
        
        self._clear_tokens()
        return False
    
    def get_current_user(self):
        return self.current_user
    
    def has_permission(self, menu_name, action='view'):
        if not self.permissions:
            return False
        
        menu_perms = self.permissions.get(menu_name, {})
        action_key = f'can_{action}'
        return menu_perms.get(action_key, False)
    
    def can_access_desa(self, desa_name):
        if not self.current_user:
            return False
        
        if self.current_user.get('role') == 'super_admin':
            return True
        
        assigned_desa = self.accessible_areas.get('desa', [])
        return desa_name in assigned_desa
    
    def can_access_kelompok(self, kelompok_name):
        if not self.current_user:
            return False
        
        if self.current_user.get('role') == 'super_admin':
            return True
        
        assigned_kelompok = self.accessible_areas.get('kelompok', [])
        return kelompok_name in assigned_kelompok
    
    def get_accessible_desa(self):
        if self.current_user and self.current_user.get('role') == 'super_admin':
            return ['BANDARA', 'CENGKARENG', 'CIPONDOH', 'JELAMBAR', 'KALIDERES', 'KEBON JAHE', 'TAMAN KOTA', 'KAPUK MELATI']
        
        return self.accessible_areas.get('desa', [])
    
    def get_accessible_kelompok(self):
        if self.current_user and self.current_user.get('role') == 'super_admin':
            return [
                "TEGAL ALUR A", "TEGAL ALUR B", "PREPEDAN A", "PREPEDAN B", "KEBON KELAPA",
                "PRIMA", "RAWA LELE", "KAMPUNG DURI", "FAJAR A", "FAJAR B", "FAJAR C",
                "DAMAI", "JAYA", "INDAH", "PEJAGALAN", "BGN", "MELATI A", "MELATI B",
                "GRIYA PERMATA", "SEMANAN A", "SEMANAN B", "PONDOK BAHAR",
                "KEBON JAHE A", "KEBON JAHE B", "GARIKAS", "TANIWAN",
                "TAMAN KOTA A", "TAMAN KOTA B", "RAWA BUAYA A", "RAWA BUAYA B"
            ]
        
        return self.accessible_areas.get('kelompok', [])