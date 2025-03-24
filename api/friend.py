import requests
import base64
from typing import Optional, List, Dict, Any, Union
from bson import ObjectId
from config import FRIEND_API, X_API_KEY

class FriendApi:
    @staticmethod
    def _make_request(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Выполняет запрос к API"""
        url = f"http://{FRIEND_API}/{endpoint}"
        headers = {"X-API-KEY": X_API_KEY}
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @classmethod
    def create_application(cls) -> Dict[str, Any]:
        """Создает новую анкету"""
        return cls._make_request("create_app")
    
    @classmethod
    def get_application_data(cls, application_id: str) -> Dict[str, Any]:
        """Получает данные анкеты"""
        return cls._make_request("get_app", {"application_id": application_id})
    
    @classmethod
    def set_application_data(cls, application_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Устанавливает данные анкеты"""
        return cls._make_request("set_app", {
            "application_id": application_id,
            "data": data
        })
    
    @classmethod
    def add_application_photo(cls, application_id: str, photo_data: bytes) -> Dict[str, Any]:
        """Добавляет фото к анкете
        
        Args:
            application_id: ID анкеты
            photo_data: байты изображения
        """
        # Кодируем фото в base64
        photo_base64 = base64.b64encode(photo_data).decode('utf-8')
        
        # Создаем JSON с данными анкеты и фотографией
        data = {
            "application_id": application_id,
            "photo": photo_base64
        }
        
        return cls._make_request("add_app_photo", data)
    
    @classmethod
    def get_application_photos_pdf(cls, application_id: str) -> Dict[str, Any]:
        """Получает фотографии анкеты в формате PDF
        
        Args:
            application_id: ID анкеты
            
        Returns:
            Словарь с полями:
            - status: статус запроса
            - pdf_base64: PDF в формате base64
            - pdf_url: URL для скачивания PDF
        """
        return cls._make_request("get_app_photo", {"application_id": application_id})
    
    @classmethod
    def clear_application_photos(cls, application_id: str) -> Dict[str, Any]:
        """Очищает фото анкеты"""
        return cls._make_request("clear_app_photo", {"application_id": application_id})
    
    @classmethod
    def delete_application(cls, application_id: str) -> Dict[str, Any]:
        """Удаляет анкету"""
        return cls._make_request("delete_app", {"application_id": application_id})
    
    @classmethod
    def get_user_apps(cls, tg_id: int) -> Dict[str, Any]:
        """Получает список анкет пользователя"""
        return cls._make_request("get_user_apps", {"tg_id": tg_id})
    
    @classmethod
    def get_facility_binds(cls) -> Dict[str, Any]:
        """Получает привязки объектов к пользователям"""
        return cls._make_request("get_facility_binds")
    
    @classmethod
    def set_facility_binds(cls, binds: List[Dict[str, str]]) -> Dict[str, Any]:
        """Устанавливает привязки объектов к пользователям"""
        return cls._make_request("set_facility_binds", {"binds": binds})
    
    @classmethod
    def get_jobs_list(cls) -> Dict[str, Any]:
        """Получает список доступных вакансий"""
        return cls._make_request("get_jobs") 