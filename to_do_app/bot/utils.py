class UserData:
    _tokens = {}

    @classmethod
    async def save_tokens(cls, user_id, access_token, refresh_token):
        cls._tokens[user_id] = (access_token, refresh_token)

    @classmethod
    async def get_tokens(cls, user_id):
        return cls._tokens.get(user_id, (None, None))

    @classmethod
    async def delete_tokens(cls, user_id):
        if user_id in cls._tokens:
            del cls._tokens[user_id]