from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

class UserData(BaseModel):
    accessToken: str
    userId: str
    userEmail: Optional[str] = None
    userName: Optional[str] = None

@app.post("/api/login")
async def login(user_data: UserData):
    try:
        # 여기서 받은 데이터를 처리합니다.
        # 예: 데이터베이스에 저장, 토큰 검증 등
        print(f"Received user data: {user_data}")

        # 네이버 액세스 토큰 검증 로직을 여기에 추가할 수 있습니다.
        # 이는 네이버 API를 사용하여 수행할 수 있습니다.

        # 사용자 정보를 데이터베이스에 저장하는 로직
        # 예: save_user_to_database(user_data)

        return {"message": "Login successful", "userId": user_data.userId}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 추가적인 엔드포인트들...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)