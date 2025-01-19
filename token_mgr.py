class TokenManager:
    def __init__(self, tokens: dict = None):
        if tokens is None:
            tokens = {}
        if not isinstance(tokens, dict):
            raise TypeError("Tokens must be a dictionary.")
        
        self.update_status = None
        self.token = None
        self.old_tokens = []  # Список для хранения старых токенов
        self.all_tokens = tokens
        
        # Сбрасываем все статусы при инициализации
        for token_info in self.all_tokens.values():
            token_info['STATUS'] = True
        
        self.valid_tokens = [value['TOKEN'] for value in self.all_tokens.values() if value['STATUS']]
        self.set_token()
    
    def set_token(self):
        if not self.valid_tokens:
            self.token = None
            self.set_update_status(False)
            return
        
        new_token = self.valid_tokens.pop(0)  # Извлекаем первый токен из списка доступных
        if new_token != self.token:
            if self.token is not None:
                self.old_tokens.append(self.token)  # Добавляем текущий токен в список старых токенов
            
            # Обновляем статус старого токена в all_tokens
            for token_key, token_info in self.all_tokens.items():
                if token_info['TOKEN'] == self.token:
                    self.all_tokens[token_key]['STATUS'] = False
                    break
            
            self.token = new_token
            self.set_update_status(True)
            return True
        else:
            self.set_update_status(False)
            return False
    
    def get_token(self):
        return self.token
    
    def set_update_status(self, status: bool = False):
        self.update_status = status
    
    def get_update_status(self, reset_status: bool = True):
        status = self.update_status
        if reset_status:
            self.set_update_status(False)
        return status
    
    def add_token(self, new_token: str):
        # Проверяем, существует ли уже такой токен
        for token_info in self.all_tokens.values():
            if token_info['TOKEN'] == new_token:
                print('Token already exists.')
                return False
        
        # Получаем новый ID, который будет больше существующих
        new_id = str(max(map(int, self.all_tokens.keys())) + 1) if self.all_tokens else "1"
        
        # Добавляем новый токен с присвоением статуса True
        self.all_tokens[new_id] = {"TOKEN": new_token, "STATUS": True}
        
        # Обновляем список валидных токенов
        self.valid_tokens.append(new_token)
        
        return True
